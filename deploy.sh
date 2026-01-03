#!/bin/bash
# Deploy helpdesk_mgmt to Hetzner Odoo 19 dev environment
# NOTE: This script does NOT push to git - do that manually first!

echo "🚀 Deploying to Hetzner dev server..."
ssh hetzner-sybren << 'EOF'
  cd /tmp
  rm -rf helpdesk_mgmt_19
  git clone -b 19.0-mig-helpdesk_mgmt https://github.com/sybdeb/helpdesk_mgmt_19.git

  # Use dev container
  ODOO_CONTAINER="odoo19-dev-web-1"

  echo "📋 Using container: $ODOO_CONTAINER"

  # Remove old module first
  echo "🗑️  Removing old module..."
  docker exec $ODOO_CONTAINER rm -rf /mnt/extra-addons/helpdesk_mgmt

  # Copy to container
  echo "📦 Copying new module..."
  docker cp /tmp/helpdesk_mgmt_19/helpdesk_mgmt $ODOO_CONTAINER:/mnt/extra-addons/

  # Restart container (no upgrade - do that manually via Odoo interface)
  echo "♻️  Restarting container..."
  docker restart $ODOO_CONTAINER

  echo "✅ Deploy complete! Don't forget to upgrade the module via Odoo interface."
EOF
