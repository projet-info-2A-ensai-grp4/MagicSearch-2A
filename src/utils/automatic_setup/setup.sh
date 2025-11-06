#!/bin/bash
# filepath: /home/victor/Work/MagicSearch-2A/src/utils/automatic_setup/setup.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get to project root
cd "$(dirname "$0")/../../.."
PROJECT_ROOT=$(pwd)

gum style \
    --border double \
    --border-foreground 212 \
    --padding "1 2" \
    --margin "1 0" \
    --align center \
    "$(gum style --foreground 212 --bold '🎴 MagicSearch Setup Wizard 🎴')"

# --- Add PYTHONPATH for this session (and optionally persist to ~/.bashrc) ---
export PYTHONPATH="$PROJECT_ROOT/src:${PYTHONPATH:-}"

echo ""
gum style --foreground 147 "PYTHONPATH set for this session: ${PYTHONPATH}"

if gum confirm "Add PYTHONPATH=\"$PROJECT_ROOT/src\" to your ~/.bashrc for future sessions?"; then
    # avoid duplicate entries
    if ! grep -Fqx "export PYTHONPATH=\"$PROJECT_ROOT/src:\$PYTHONPATH\"" ~/.bashrc 2>/dev/null; then
        printf "\n# MagicSearch PYTHONPATH\nexport PYTHONPATH=\"$PROJECT_ROOT/src:\$PYTHONPATH\"\n" >> ~/.bashrc
        gum style --foreground 82 "✓ PYTHONPATH added to ~/.bashrc"
    else
        gum style --foreground 246 "PYTHONPATH already present in ~/.bashrc"
    fi
fi


# ============================================================================
# STEP 1: Check Dependencies
# ============================================================================

gum style --border rounded --border-foreground 212 --padding "1 2" --margin "1 0" \
    "$(gum style --foreground 212 '📋 Step 1: Checking Dependencies')"

check_dependency() {
    local cmd=$1
    local name=$2
    if command -v $cmd &> /dev/null; then
        gum style --foreground 82 "✓ $name installed"
        return 0
    else
        gum style --foreground 196 "✗ $name not found"
        return 1
    fi
}

MISSING_DEPS=0

check_dependency "gum" "Gum" || MISSING_DEPS=1
check_dependency "python3" "Python 3" || MISSING_DEPS=1
check_dependency "psql" "PostgreSQL Client" || MISSING_DEPS=1

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    gum style --foreground 196 "❌ Missing dependencies detected!"
    echo ""
    gum style --foreground 220 "Please install missing dependencies:"
    echo ""
    gum style --foreground 246 "• Gum: https://github.com/charmbracelet/gum#installation"
    gum style --foreground 246 "• Python 3: sudo apt install python3 python3-pip python3-venv"
    gum style --foreground 246 "• PostgreSQL: sudo apt install postgresql postgresql-contrib"
    exit 1
fi

echo ""
gum style --foreground 82 "✨ All dependencies installed!"
sleep 1

# ============================================================================
# STEP 2: Python Dependencies
# ============================================================================

echo ""
gum style --border rounded --border-foreground 212 --padding "1 2" --margin "1 0" \
    "$(gum style --foreground 212 '🐍 Step 2: Python Dependencies')"

if [ ! -f "requirements.txt" ]; then
    gum style --foreground 196 "❌ requirements.txt not found in project root!"
    exit 1
fi

echo ""
gum style --foreground 147 "📦 Found requirements.txt"
gum style --foreground 246 "Dependencies will be installed using pip"
echo ""

if gum confirm "Install Python dependencies?"; then
    gum spin --spinner dot --title "Installing dependencies..." -- \
        python3 -m pip install -r requirements.txt --user
    echo ""
    gum style --foreground 82 "✓ Dependencies installed successfully!"
else
    gum style --foreground 220 "⚠️  Skipping dependency installation"
    if ! gum confirm "Continue without installing dependencies?"; then
        exit 0
    fi
fi

sleep 1

# ============================================================================
# STEP 3: Database Setup
# ============================================================================

echo ""
gum style --border rounded --border-foreground 212 --padding "1 2" --margin "1 0" \
    "$(gum style --foreground 212 '🗄️  Step 3: Database Configuration')"

echo ""
if gum confirm "Do you already have PostgreSQL configured for this project?"; then
    gum style --foreground 82 "✓ Using existing database"
    echo ""
    gum style --foreground 147 "Please provide your database credentials:"
    
    DB_HOST=$(gum input --placeholder "Database host (default: localhost)" --value "localhost")
    DB_PORT=$(gum input --placeholder "Database port (default: 5432)" --value "5432")
    DB_NAME=$(gum input --placeholder "Database name (default: magicsearch)" --value "magicsearch")
    DB_USER=$(gum input --placeholder "Database user (default: postgres)" --value "postgres")
    DB_PASSWORD=$(gum input --placeholder "Database password" --password)
    
else
    echo ""
    gum style --foreground 147 "🔧 Let's set up a new database!"
    echo ""
    
    DB_HOST=$(gum input --placeholder "Database host (default: localhost)" --value "localhost")
    DB_PORT=$(gum input --placeholder "Database port (default: 5432)" --value "5432")
    DB_NAME=$(gum input --placeholder "Database name (default: magicsearch)" --value "magicsearch")
    DB_USER=$(gum input --placeholder "Database user (default: postgres)" --value "postgres")
    DB_PASSWORD=$(gum input --placeholder "Database password" --password)
    
    echo ""
    gum style --foreground 147 "Creating database..."
    
    # Try to create database
    export PGPASSWORD="$DB_PASSWORD"
    if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "CREATE DATABASE $DB_NAME;" 2>/dev/null; then
        gum style --foreground 82 "✓ Database created successfully!"
    else
        gum style --foreground 220 "⚠️  Database might already exist or creation failed"
        if ! gum confirm "Continue anyway?"; then
            exit 1
        fi
    fi
    unset PGPASSWORD
fi

# Create .env file
echo ""
gum spin --spinner dot --title "Creating .env file..." -- sleep 1

cat > .env << EOF
# Database Configuration
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
EOF

gum style --foreground 82 "✓ .env file created in project root"

# Enable pgvector extension
echo ""
gum style --foreground 147 "📐 Enabling pgvector extension..."

export PGPASSWORD="$DB_PASSWORD"
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS vector;" 2>&1 | tee /tmp/pgvector.log; then
    gum style --foreground 82 "✓ pgvector extension enabled!"
else
    gum style --foreground 196 "❌ Failed to enable pgvector extension"
    echo ""
    gum style --foreground 220 "⚠️  You may need to install pgvector first:"
    echo ""
    gum style --foreground 246 "Ubuntu/Debian:"
    gum style --foreground 246 "  sudo apt install postgresql-<version>-pgvector"
    echo ""
    gum style --foreground 246 "Or compile from source:"
    gum style --foreground 246 "  git clone https://github.com/pgvector/pgvector.git"
    gum style --foreground 246 "  cd pgvector && make && sudo make install"
    echo ""
    cat /tmp/pgvector.log
    if ! gum confirm "Continue without pgvector? (embeddings won't work)"; then
        exit 1
    fi
fi
unset PGPASSWORD

# ============================================================================
# STEP 4: Card Data Setup
# ============================================================================

echo ""
gum style --border rounded --border-foreground 212 --padding "1 2" --margin "1 0" \
    "$(gum style --foreground 212 '🃏 Step 4: Card Data Setup')"

echo ""
gum style --foreground 147 "We need AtomicCards.json to populate the database"
echo ""

DATA_SOURCE=$(gum choose "Download AtomicCards.json" "I have the file locally")

if [ "$DATA_SOURCE" = "Download AtomicCards.json" ]; then
    mkdir -p data
    echo ""
    gum style --foreground 147 "📥 Downloading AtomicCards.json (this may take a while)..."
    
    if gum spin --spinner dot --title "Downloading..." -- \
        wget -q -O data/AtomicCards.json https://mtgjson.com/api/v5/AtomicCards.json; then
        gum style --foreground 82 "✓ Download complete!"
        CARD_DATA_PATH="$PROJECT_ROOT/data/AtomicCards.json"
    else
        gum style --foreground 196 "❌ Download failed!"
        exit 1
    fi
else
    echo ""
    CARD_DATA_PATH=$(gum input --placeholder "Enter full path to AtomicCards.json")
    
    if [ ! -f "$CARD_DATA_PATH" ]; then
        gum style --foreground 196 "❌ File not found: $CARD_DATA_PATH"
        exit 1
    fi
    gum style --foreground 82 "✓ File found!"
fi

# Initialize database tables
echo ""
gum style --foreground 147 "🔨 Initializing database tables..."

# Update init_card_table.py with correct path
INIT_SCRIPT="$PROJECT_ROOT/src/utils/automatic_setup/init_card_table_temp.py"

cat > "$INIT_SCRIPT" << 'EOFPYTHON'
import json
from psycopg2.extras import execute_values
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.utils.automatic_setup.dbConnection import dbConnection

card_data_path = sys.argv[1]

# Load JSON file
with open(card_data_path, "r") as file:
    data = json.load(file)

cards = data["data"]

rows = []
for card_key, card_list in cards.items():
    if not card_list:
        continue
    card = card_list[0]

    rows.append(
        (
            card_key,
            card.get("name"),
            card.get("asciiName"),
            card.get("text"),
            card.get("type"),
            card.get("layout"),
            card.get("manaCost"),
            card.get("manaValue"),
            card.get("convertedManaCost"),
            card.get("faceConvertedManaCost"),
            card.get("faceManaValue"),
            card.get("faceName"),
            card.get("firstPrinting"),
            card.get("hand"),
            card.get("life"),
            card.get("loyalty"),
            card.get("power"),
            card.get("toughness"),
            card.get("side"),
            card.get("defense"),
            card.get("edhrecRank"),
            card.get("edhrecSaltiness"),
            card.get("isFunny"),
            card.get("isGameChanger"),
            card.get("isReserved"),
            card.get("hasAlternativeDeckLimit"),
            card.get("colors"),
            card.get("colorIdentity"),
            card.get("colorIndicator"),
            card.get("types"),
            card.get("subtypes"),
            card.get("supertypes"),
            card.get("keywords"),
            card.get("subsets"),
            card.get("printings"),
            card.get("identifiers", {}).get("scryfallOracleId"),
            json.dumps(card),
        )
    )

with dbConnection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS cards (
            id SERIAL PRIMARY KEY,
            card_key TEXT UNIQUE,
            name TEXT,
            ascii_name TEXT,
            text TEXT,
            type TEXT,
            layout TEXT,
            mana_cost TEXT,
            mana_value NUMERIC,
            converted_mana_cost NUMERIC,
            face_converted_mana_cost NUMERIC,
            face_mana_value NUMERIC,
            face_name TEXT,
            first_printing TEXT,
            hand TEXT,
            life TEXT,
            loyalty TEXT,
            power TEXT,
            toughness TEXT,
            side TEXT,
            defense TEXT,
            edhrec_rank NUMERIC,
            edhrec_saltiness NUMERIC,
            is_funny BOOLEAN,
            is_game_changer BOOLEAN,
            is_reserved BOOLEAN,
            has_alternative_deck_limit BOOLEAN,
            colors TEXT[],
            color_identity TEXT[],
            color_indicator TEXT[],
            types TEXT[],
            subtypes TEXT[],
            supertypes TEXT[],
            keywords TEXT[],
            subsets TEXT[],
            printings TEXT[],
            scryfall_oracle_id UUID,
            image_url TEXT,
            text_to_embed TEXT,
            embedding VECTOR,
            raw JSONB
        )
        """)

        execute_values(
            cur,
            """
            INSERT INTO cards (
                card_key, name, ascii_name, text, type, layout, mana_cost, mana_value,
                converted_mana_cost, face_converted_mana_cost, face_mana_value, face_name,
                first_printing, hand, life, loyalty, power, toughness, side, defense,
                edhrec_rank, edhrec_saltiness, is_funny, is_game_changer, is_reserved,
                has_alternative_deck_limit, colors, color_identity, color_indicator,
                types, subtypes, supertypes, keywords, subsets, printings,
                scryfall_oracle_id, raw
            ) VALUES %s
            ON CONFLICT (card_key) DO NOTHING
            """,
            rows,
        )
    conn.commit()

print(f"✓ Inserted {len(rows)} cards into database")
EOFPYTHON

if gum spin --spinner dot --title "Creating cards table..." -- \
    python3 "$INIT_SCRIPT" "$CARD_DATA_PATH" 2>&1 | tee /tmp/init_cards.log; then
    gum style --foreground 82 "✓ Cards table created and populated!"
else
    gum style --foreground 196 "❌ Failed to initialize cards table"
    cat /tmp/init_cards.log
    exit 1
fi

rm "$INIT_SCRIPT"

# Initialize other tables
echo ""
gum style --foreground 147 "🔨 Creating other tables..."

# Create temporary script for other tables
OTHER_TABLES_SCRIPT="$PROJECT_ROOT/src/utils/automatic_setup/init_other_tables_temp.py"

cat > "$OTHER_TABLES_SCRIPT" << 'EOFPYTHON'
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.utils.automatic_setup.dbConnection import dbConnection

with dbConnection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            role_id SERIAL PRIMARY KEY,
            role_name VARCHAR(50) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(150) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role_id INT NOT NULL,
            FOREIGN KEY (role_id) REFERENCES roles(role_id)
        );

        CREATE TABLE IF NOT EXISTS decks (
            deck_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(100),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        CREATE TABLE IF NOT EXISTS deck_cards (
            deck_id INT NOT NULL,
            card_id INT NOT NULL,
            quantity INT DEFAULT 1,
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id),
            FOREIGN KEY (card_id) REFERENCES cards(id)
        );

        CREATE TABLE IF NOT EXISTS user_deck_link (
            user_id INT NOT NULL,
            deck_id INT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (deck_id) REFERENCES decks(deck_id)
        );

        CREATE TABLE IF NOT EXISTS favorites (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            card_id INT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, card_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (card_id) REFERENCES cards(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS histories (
            history_id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            prompt TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );

        -- Insert default roles
        INSERT INTO roles (role_id, role_name) VALUES
            (0, 'player'),
            (1, 'admin')
        ON CONFLICT (role_id) DO NOTHING;
        """)
    conn.commit()

print("✓ All tables created successfully")
EOFPYTHON

if gum spin --spinner dot --title "Creating other tables..." -- \
    python3 "$OTHER_TABLES_SCRIPT" 2>&1 | tee /tmp/init_other_tables.log; then
    gum style --foreground 82 "✓ All tables created successfully!"
else
    gum style --foreground 196 "❌ Failed to initialize other tables"
    cat /tmp/init_other_tables.log
    exit 1
fi

rm "$OTHER_TABLES_SCRIPT"

sleep 1

# ============================================================================
# STEP 5: Optional Enhancements
# ============================================================================

echo ""
gum style --border rounded --border-foreground 212 --padding "1 2" --margin "1 0" \
    "$(gum style --foreground 212 '✨ Step 5: Optional Enhancements')"

echo ""
gum style --foreground 147 "Choose what you want to set up (use x to select, Enter to confirm):"
echo ""

ENHANCEMENTS=$(gum choose --no-limit "Download card images" "Generate embeddings")

# Check if user selected nothing
if [ -z "$ENHANCEMENTS" ]; then
    gum style --foreground 246 "⏭️  Skipping enhancements"
    sleep 1
else
    # Download images
    if echo "$ENHANCEMENTS" | grep -q "Download card images"; then
        echo ""
        gum style --foreground 147 "🖼️  Starting image download process..."
        gum style --foreground 246 "This will fetch card images from Scryfall API"
        echo ""
        
        cd src/utils/automatic_setup
        if gum spin --spinner dot --title "Downloading images (this may take a while)..." -- \
            python3 add_img.py 2>&1 | tee /tmp/add_img.log; then
            cd "$PROJECT_ROOT"
            gum style --foreground 82 "✓ Image download complete!"
        else
            cd "$PROJECT_ROOT"
            gum style --foreground 220 "⚠️  Image download encountered issues"
            gum style --foreground 246 "You can resume later by running: python3 src/utils/automatic_setup/add_img.py"
        fi
    fi

    # Generate embeddings
    if echo "$ENHANCEMENTS" | grep -q "Generate embeddings"; then
        echo ""
        gum style --foreground 147 "🧠 Setting up embeddings..."
        echo ""
        
        gum style --foreground 147 "Please enter your SSPCloud API key:"
        LLM_API_KEY=$(gum input --placeholder "API Key" --password)
        
        # Add to .env
        echo "LLM_API_KEY=$LLM_API_KEY" >> .env
        
        gum style --foreground 82 "✓ API key saved to .env"
        echo ""
        
        gum style --foreground 147 "🚀 Starting embedding generation..."
        gum style --foreground 246 "This will take a significant amount of time"
        echo ""
        
        cd src/utils/automatic_setup
        if gum confirm "Start embedding process now?"; then
            if gum spin --spinner dot --title "Generating embeddings..." -- \
                python3 vectorize.py 2>&1 | tee /tmp/vectorize.log; then
                cd "$PROJECT_ROOT"
                gum style --foreground 82 "✓ Embeddings generated successfully!"
            else
                cd "$PROJECT_ROOT"
                gum style --foreground 220 "⚠️  Embedding generation interrupted or failed"
                gum style --foreground 246 "You can resume later by running: python3 src/utils/automatic_setup/vectorize.py"
            fi
        else
            cd "$PROJECT_ROOT"
            gum style --foreground 246 "Skipped. Run later with: python3 src/utils/automatic_setup/vectorize.py"
        fi
    fi
fi

sleep 1

# ============================================================================
# STEP 6: API Configuration
# ============================================================================

echo ""
gum style --border rounded --border-foreground 212 --padding "1 2" --margin "1 0" \
    "$(gum style --foreground 212 '🔗 Step 6: API Configuration')"

echo ""
gum style --foreground 147 "Configure your API URL for the frontend"
echo ""

API_URL=$(gum input --placeholder "API URL (default: http://localhost:8000)" --value "http://localhost:8000")

# Create config.js file
CONFIG_JS="$PROJECT_ROOT/src/static/config.js"

cat > "$CONFIG_JS" << EOF
// filepath: /home/victor/Work/MagicSearch-2A/src/static/config.js
// Auto-generated API configuration
const API_CONFIG = {
    BASE_URL: '${API_URL}'
};
EOF

gum style --foreground 82 "✓ API configuration saved to src/static/config.js"
echo ""
gum style --foreground 246 "API URL: $API_URL"

# ============================================================================
# STEP 7: Launch Services
# ============================================================================

echo ""
gum style --border rounded --border-foreground 212 --padding "1 2" --margin "1 0" \
    "$(gum style --foreground 212 '🚀 Step 7: Launch Services')"

echo ""
if gum confirm "Start FastAPI backend and HTTP server?"; then
    
    # Start FastAPI
    gum style --foreground 147 "Starting FastAPI backend..."
    python3 src > /tmp/fastapi.log 2>&1 &
    FASTAPI_PID=$!
    sleep 2
    
    if ps -p $FASTAPI_PID > /dev/null; then
        gum style --foreground 82 "✓ FastAPI started (PID: $FASTAPI_PID)"
    else
        gum style --foreground 196 "❌ FastAPI failed to start"
        cat /tmp/fastapi.log
        exit 1
    fi
    
    # Start HTTP server
    gum style --foreground 147 "Starting HTTP server on port 8001..."
    cd src
    python3 -m http.server 8001 > /tmp/http_server.log 2>&1 &
    HTTP_PID=$!
    cd "$PROJECT_ROOT"
    sleep 1
    
    if ps -p $HTTP_PID > /dev/null; then
        gum style --foreground 82 "✓ HTTP server started (PID: $HTTP_PID)"
    else
        gum style --foreground 196 "❌ HTTP server failed to start"
        cat /tmp/http_server.log
        exit 1
    fi
    
    echo ""
    gum style --border double --border-foreground 82 --padding "1 2" --margin "1 0" \
        "$(gum style --foreground 82 --bold '✨ Setup Complete! ✨')"
    
    echo ""
    gum style --foreground 147 "📊 Service Information:"
    echo ""
    gum style --foreground 246 "• FastAPI Backend:"
    gum style --foreground 246 "  - PID: $FASTAPI_PID"
    gum style --foreground 246 "  - Logs: /tmp/fastapi.log"
    echo ""
    gum style --foreground 246 "• HTTP Server:"
    gum style --foreground 246 "  - PID: $HTTP_PID"
    gum style --foreground 246 "  - Port: 8001"
    gum style --foreground 246 "  - Logs: /tmp/http_server.log"
    echo ""
    gum style --foreground 220 "🛑 To stop services:"
    gum style --foreground 246 "  kill $FASTAPI_PID $HTTP_PID"
    
else
    echo ""
    gum style --border double --border-foreground 82 --padding "1 2" --margin "1 0" \
        "$(gum style --foreground 82 --bold '✨ Setup Complete! ✨')"
    
    echo ""
    gum style --foreground 147 "To start services manually:"
    echo ""
    gum style --foreground 246 "• FastAPI: python3 src"
    gum style --foreground 246 "• HTTP Server: cd src && python3 -m http.server 8001"
fi

echo ""
gum style --foreground 212 "🎴 Happy Magic searching! 🎴"