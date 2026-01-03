#!/bin/bash
# Deploy helpdesk_mgmt to Hetzner Odoo 19 PRODUCTION environment
# ⚠️  WARNING: This deploys to PRODUCTION! Use with caution!
# NOTE: This script does NOT push to git - do that manually first!

echo "⚠️  ============================================"
echo "⚠️  WARNING: Deploying to PRODUCTION!"
echo "⚠️  ============================================"
echo ""
read -p "Are you sure you want to deploy to PRODUCTION? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled."
    exit 1
fi

echo ""
echo "🚀 Deploying to Hetzner PRODUCTION server..."
ssh hetzner-sybren << 'EOF'
  cd /tmp
  rm -rf helpdesk_mgmt_19
  git clone -b 19.0-mig-helpdesk_mgmt https://github.com/sybdeb/helpdesk_mgmt_19.git

  # Use PRODUCTION container
  ODOO_CONTAINER="odoo19-prod-web-1"

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

  echo ""
  echo "✅ PRODUCTION deploy complete!"
  echo ""
  echo "⚠️  IMPORTANT: You must manually upgrade the module via Odoo interface:"
  echo "   1. Go to Apps menu"
  echo "   2. Search for 'Helpdesk Management'"
  echo "   3. Click 'Upgrade'"
  echo ""
EOF

echo ""
echo "🎉 Production deployment finished!"
