#!/bin/bash

# Скрипт для переключения между режимами docker-compose
# Использование:
#   ./switch-mode.sh local  - локальная сборка образов
#   ./switch-mode.sh prod   - использование образов из registry

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEVOPS_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

MODE="$1"

# Цвета для вывода
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_usage() {
    echo "Использование: $0 {local|prod}"
    echo ""
    echo "Режимы:"
    echo "  local  - Локальная сборка образов (build from source)"
    echo "  prod   - Использование образов из GitHub Container Registry"
    echo ""
    echo "Примеры:"
    echo "  $0 local   # Переключиться на локальную сборку"
    echo "  $0 prod    # Переключиться на production образы"
}

switch_to_local() {
    echo -e "${BLUE}Переключение в режим LOCAL (локальная сборка)...${NC}"

    cd "$DEVOPS_DIR"

    # Создаем симлинк на docker-compose.yml
    if [ -L "docker-compose.current.yml" ] || [ -f "docker-compose.current.yml" ]; then
        rm -f docker-compose.current.yml
    fi

    ln -s docker-compose.yml docker-compose.current.yml

    echo -e "${GREEN}✓ Режим LOCAL активирован${NC}"
    echo ""
    echo "Теперь используется: docker-compose.yml (локальная сборка)"
    echo ""
    echo "Команды для запуска:"
    echo "  cd devops"
    echo "  docker-compose -f docker-compose.current.yml up --build"
}

switch_to_prod() {
    echo -e "${BLUE}Переключение в режим PROD (registry образы)...${NC}"

    cd "$DEVOPS_DIR"

    # Создаем симлинк на docker-compose.prod.yml
    if [ -L "docker-compose.current.yml" ] || [ -f "docker-compose.current.yml" ]; then
        rm -f docker-compose.current.yml
    fi

    ln -s docker-compose.prod.yml docker-compose.current.yml

    echo -e "${GREEN}✓ Режим PROD активирован${NC}"
    echo ""
    echo "Теперь используется: docker-compose.prod.yml (registry образы)"
    echo ""
    echo "Команды для запуска:"
    echo "  cd devops"
    echo "  docker-compose -f docker-compose.current.yml pull  # Скачать образы"
    echo "  docker-compose -f docker-compose.current.yml up    # Запустить"
    echo ""
    echo "Для использования конкретной версии:"
    echo "  IMAGE_TAG=sha-abc1234 docker-compose -f docker-compose.current.yml up"
}

show_current_mode() {
    cd "$DEVOPS_DIR"

    if [ -L "docker-compose.current.yml" ]; then
        TARGET=$(readlink docker-compose.current.yml)
        echo -e "${BLUE}Текущий режим:${NC}"

        if [ "$TARGET" = "docker-compose.yml" ]; then
            echo -e "${GREEN}  LOCAL${NC} (локальная сборка)"
        elif [ "$TARGET" = "docker-compose.prod.yml" ]; then
            echo -e "${GREEN}  PROD${NC} (registry образы)"
        else
            echo -e "${YELLOW}  Неизвестный режим: $TARGET${NC}"
        fi
    else
        echo -e "${YELLOW}Режим не установлен (симлинк не создан)${NC}"
        echo "Запустите: $0 local  или  $0 prod"
    fi
}

# Главная логика
case "$MODE" in
    local)
        switch_to_local
        ;;
    prod)
        switch_to_prod
        ;;
    status|current|"")
        show_current_mode
        ;;
    -h|--help|help)
        print_usage
        ;;
    *)
        echo -e "${RED}Ошибка: Неизвестный режим '$MODE'${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac

