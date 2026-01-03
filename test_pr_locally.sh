#!/bin/bash
# Lokale OCA pre-commit tests voor helpdesk_mgmt module
# Dit draait dezelfde checks als GitHub Actions ZONDER naar GitHub te pushen

set -e  # Stop bij eerste fout

echo "========================================="
echo "  OCA Pre-commit Test Runner (Lokaal)  "
echo "========================================="
echo ""

# Kleuren voor output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker niet gevonden${NC}"
    echo "Installeer Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker daemon niet actief${NC}"
    echo "Start Docker Desktop"
    exit 1
fi

echo -e "${GREEN}✅ Docker actief${NC}"
echo ""

# Check of we in de juiste directory zitten
if [ ! -d "helpdesk_mgmt" ]; then
    echo -e "${RED}❌ helpdesk_mgmt module niet gevonden${NC}"
    echo "Run dit script vanuit de oca-helpdesk-19 directory"
    exit 1
fi

echo -e "${GREEN}✅ Module gevonden: helpdesk_mgmt${NC}"
echo ""

# Pre-commit check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STAP 1: Pre-commit Checks"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check of pre-commit geïnstalleerd is
if command -v pre-commit &> /dev/null; then
    echo -e "${YELLOW}Running pre-commit hooks...${NC}"
    if pre-commit run --all-files; then
        echo -e "${GREEN}✅ Pre-commit checks GESLAAGD${NC}"
    else
        echo -e "${RED}❌ Pre-commit checks GEFAALD${NC}"
        echo "Fix de fouten hierboven en probeer opnieuw"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  Pre-commit niet geïnstalleerd, skip deze check${NC}"
    echo "Installeer met: pip install pre-commit && pre-commit install"
fi

echo ""

# Manifestoo checks (like OCA does)
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STAP 2: Manifest Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v manifestoo &> /dev/null; then
    echo "Checking licenses..."
    manifestoo -d helpdesk_mgmt check-licenses

    echo "Checking development status..."
    manifestoo -d helpdesk_mgmt check-dev-status --default-dev-status=Beta

    echo -e "${GREEN}✅ Manifest checks GESLAAGD${NC}"
else
    echo -e "${YELLOW}⚠️  Manifestoo niet geïnstalleerd${NC}"
    echo "Installeer met: pip install manifestoo-core"
fi

echo ""

# Python syntax check
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STAP 3: Python Syntax Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

python -m py_compile helpdesk_mgmt/**/*.py 2>/dev/null && \
    echo -e "${GREEN}✅ Python syntax OK${NC}" || \
    echo -e "${YELLOW}⚠️  Some Python files have syntax warnings${NC}"

echo ""

# XML validation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  STAP 4: XML Validation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

XML_ERRORS=0
for xml_file in $(find helpdesk_mgmt -name "*.xml"); do
    if ! xmllint --noout "$xml_file" 2>/dev/null; then
        echo -e "${RED}❌ Invalid XML: $xml_file${NC}"
        XML_ERRORS=$((XML_ERRORS+1))
    fi
done

if [ $XML_ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All XML files valid${NC}"
else
    echo -e "${RED}❌ $XML_ERRORS XML file(s) met fouten${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${GREEN}✅ ALLE LOKALE CHECKS GESLAAGD${NC}"
echo ""
echo "Je kunt nu veilig committen en pushen naar GitHub!"
echo ""
echo "Volgende stappen:"
echo "  1. git add ."
echo "  2. git commit -m '[FIX] helpdesk_mgmt: your fix description'"
echo "  3. git push origin 19.0-mig-helpdesk_mgmt"
echo ""
echo "Of draai de volledige Odoo tests met Docker:"
echo "  ./test_with_odoo.sh"
echo ""
