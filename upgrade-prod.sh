#!/bin/bash

set -Eeuxo pipefail

nginx_service_name=nginx-production

reload_nginx() {  
    docker compose exec "$nginx_service_name" \
        /usr/sbin/nginx -s reload
}

scale_service() {
    local service_name scale_num
    service_name="$1"
    scale_num="$2"
    docker compose up \
        --detach \
        --no-deps \
        --no-recreate \
        --scale "$service_name=$scale_num" \
        "$service_name"
}

get_container_ids() {
    local service_name
    service_name="$1"
    docker ps -f "name=$service_name" -q
}

get_container_ip() {
    local container_id
    container_id="$1"
    docker inspect \
        -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
        "$container_id"
}

kill_container() {
    local container_id
    container_id="$1"
    docker stop "$container_id"
    docker rm "$container_id"
}

get_allowed_host() {
    local host
    host=$(\
        grep '^ALLOWED_HOSTS=' "${ENV_FILE:-.env}" | \
        sed 's/[^=]*=\(.*\)/\1/'                   | \
        cut -d ',' -f1                               \
    )
    [ -n "$host" ] && echo "$host" || echo 'localhost'
}

wait_for_container() {
    local container_id http_port container_ip
    container_id="$1"
    http_port="$2"
    container_ip=$(get_container_ip "$container_id")
    curl \
        --fail \
        --head \
        --header "Host: $(get_allowed_host)" \
        --output /dev/null \
        --retry 30 \
        --retry-connrefused \
        --retry-delay 1 \
        --silent \
        "http://$container_ip:$http_port/" \
    || exit 1
}

# https://tendenci.readthedocs.io/en/latest/upgrade/point-update.html
run_tendenci_upgrade() {  
    local service_name
    service_name="$1"
    docker compose \
        run \
            --build \
            --no-deps \
            --rm \
        "$service_name" \
            /bin/bash -c " \
                echo 'Running Tendenci upgrade' \
                && python3 manage.py add_settings \
                    --json ../m4l-tendenci/tendenci/apps/chapter_pages/settings.json \
                && python3 manage.py migrate \
                && python3 manage.py deploy \
                && python3 manage.py clear_cache \
            "
}

zero_downtime_cutover() {  
    local service_name service_http_port old_container_id new_container_id
    service_name="$1"
    service_http_port="$2"

    # capture the container id running the old version of the service
    old_container_id=$(get_container_ids "$service_name" | tail -n1)

    # bring a new container online, running the new version
    # (nginx continues routing to the old container only)  
    scale_service "$service_name" 2

    # wait for the new container to start responding to requests 
    new_container_id=$(get_container_ids "$service_name" | head -n1)
    wait_for_container "$new_container_id" "$service_http_port"

    # start routing requests to the new container (as well as the old)  
    reload_nginx

    # take the old container offline  
    kill_container "$old_container_id"
    scale_service "$service_name" 1

    # stop routing requests to the old container  
    reload_nginx
}

# rebuild the container and run migrations
run_tendenci_upgrade tendenci-production
# switch over to the new tendenci container
zero_downtime_cutover tendenci-production 8000
