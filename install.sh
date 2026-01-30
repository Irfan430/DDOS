#!/bin/bash

# XPRO DDOS Toolkit - Installation Script (Linux/macOS)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
print_banner() {
    clear
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗"
    echo -e "${RED}║                                                              ║"
    echo -e "${RED}║  ${CYAN}██╗  ██╗${YELLOW}██████╗ ${GREEN}█████╗  ${MAGENTA}██████╗  ${WHITE}██████╗  ${RED}║"
    echo -e "${RED}║  ${CYAN}╚██╗██╔╝${YELLOW}██╔══██╗${GREEN}██╔══██╗${MAGENTA}██╔═══██╗${WHITE}██╔══██╗ ${RED}║"
    echo -e "${RED}║  ${CYAN} ╚███╔╝ ${YELLOW}██████╔╝${GREEN}███████║${MAGENTA}██║   ██║${WHITE}██████╔╝ ${RED}║"
    echo -e "${RED}║  ${CYAN} ██╔██╗ ${YELLOW}██╔═══╝ ${GREEN}██╔══██║${MAGENTA}██║   ██║${WHITE}██╔══██╗ ${RED}║"
    echo -e "${RED}║  ${CYAN}██╔╝ ██╗${YELLOW}██║     ${GREEN}██║  ██║${MAGENTA}╚██████╔╝${WHITE}██║  ██║ ${RED}║"
    echo -e "${RED}║  ${CYAN}╚═╝  ╚═╝${YELLOW}╚═╝     ${GREEN}╚═╝  ╚═╝${MAGENTA} ╚═════╝ ${WHITE}╚═╝  ╚═╝ ${RED}║"
    echo -e "${RED}║                                                              ║"
    echo -e "${RED}║         ${WHITE}Installation Script v1.0 (Linux/macOS)       ${RED}║"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        echo -e "${YELLOW}[!] Warning: Running as root${NC}"
        read -p "Continue? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Check Python version
check_python() {
    echo -e "${CYAN}[*] Checking Python version...${NC}"
    
    if command -v python3 &>/dev/null; then
        PYTHON_CMD="python3"
        echo -e "${GREEN}[+] Python3 found${NC}"
    elif command -v python &>/dev/null; then
        python_version=$(python --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1)
        if [[ $python_version -eq 3 ]]; then
            PYTHON_CMD="python"
            echo -e "${GREEN}[+] Python3 found${NC}"
        else
            echo -e "${RED}[!] Python3 is required${NC}"
            exit 1
        fi
    else
        echo -e "${RED}[!] Python3 not found${NC}"
        echo -e "${YELLOW}[*] Installing Python3...${NC}"
        
        # Detect OS and install Python
        if [[ -f /etc/debian_version ]]; then
            sudo apt update && sudo apt install -y python3 python3-pip
        elif [[ -f /etc/redhat-release ]]; then
            sudo yum install -y python3 python3-pip
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install python3
        else
            echo -e "${RED}[!] Cannot auto-install Python3${NC}"
            echo -e "${YELLOW}[*] Please install Python3 manually${NC}"
            exit 1
        fi
        
        PYTHON_CMD="python3"
    fi
}

# Check pip
check_pip() {
    echo -e "${CYAN}[*] Checking pip...${NC}"
    
    if ! command -v pip3 &>/dev/null && ! command -v pip &>/dev/null; then
        echo -e "${YELLOW}[!] pip not found. Installing...${NC}"
        
        if [[ "$PYTHON_CMD" == "python3" ]]; then
            curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            sudo $PYTHON_CMD get-pip.py
            rm get-pip.py
        fi
    fi
    
    echo -e "${GREEN}[+] pip is ready${NC}"
}

# Install requirements
install_requirements() {
    echo -e "${CYAN}[*] Installing Python packages...${NC}"
    
    if [[ -f "requirements.txt" ]]; then
        if command -v pip3 &>/dev/null; then
            pip3 install -r requirements.txt
        elif command -v pip &>/dev/null; then
            pip install -r requirements.txt
        else
            echo -e "${RED}[!] pip not available${NC}"
            exit 1
        fi
        
        if [[ $? -eq 0 ]]; then
            echo -e "${GREEN}[+] Packages installed successfully${NC}"
        else
            echo -e "${YELLOW}[!] Some packages may not have installed${NC}"
        fi
    else
        echo -e "${RED}[!] requirements.txt not found${NC}"
        exit 1
    fi
}

# Check main files
check_files() {
    echo -e "${CYAN}[*] Checking required files...${NC}"
    
    local missing_files=()
    
    for file in "main.py" "requirements.txt"; do
        if [[ ! -f "$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo -e "${RED}[!] Missing files: ${missing_files[*]}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}[+] All files found${NC}"
}

# Make executable
make_executable() {
    echo -e "${CYAN}[*] Setting permissions...${NC}"
    
    chmod +x main.py
    
    # Create launcher script
    cat > xpro << 'EOF'
#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"
python3 main.py "$@"
EOF
    
    chmod +x xpro
    
    echo -e "${GREEN}[+] Created launcher: ./xpro${NC}"
}

# Add to PATH (optional)
add_to_path() {
    echo -e "${CYAN}[*] Add to PATH? (y/n): ${NC}" 
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        local bin_dir="$HOME/bin"
        
        mkdir -p "$bin_dir"
        cp xpro "$bin_dir/"
        
        # Check if bin is in PATH
        if [[ ":$PATH:" != *":$bin_dir:"* ]]; then
            echo -e "${YELLOW}[*] Adding $bin_dir to PATH...${NC}"
            
            # Detect shell
            if [[ "$SHELL" == *"zsh"* ]]; then
                echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
                echo -e "${GREEN}[+] Added to ~/.zshrc${NC}"
                echo -e "${YELLOW}[*] Run: source ~/.zshrc${NC}"
            elif [[ "$SHELL" == *"bash"* ]]; then
                echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
                echo -e "${GREEN}[+] Added to ~/.bashrc${NC}"
                echo -e "${YELLOW}[*] Run: source ~/.bashrc${NC}"
            fi
        fi
        
        echo -e "${GREEN}[+] You can now run 'xpro' from anywhere${NC}"
    fi
}

# Show usage
show_usage() {
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}INSTALLATION COMPLETE!${NC}"
    echo -e "${CYAN}══════════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${YELLOW}USAGE:${NC}"
    echo -e "  ${CYAN}./xpro${NC}                         # Interactive mode"
    echo -e "  ${CYAN}./xpro -t target.com${NC}           # With target"
    echo -e "  ${CYAN}python3 main.py${NC}                # Direct Python"
    
    echo -e "\n${YELLOW}EXAMPLES:${NC}"
    echo -e "  ${CYAN}./xpro -t example.com -p 80 -m http -th 500 -d 60${NC}"
    echo -e "  ${CYAN}./xpro -t 192.168.1.1 -m slowloris${NC}"
    
    echo -e "\n${YELLOW}ARGUMENTS:${NC}"
    echo -e "  -t, --target    Target IP/domain"
    echo -e "  -p, --port      Port (default: 80)"
    echo -e "  -m, --method    http/slowloris/udp"
    echo -e "  -th, --threads  Thread count"
    echo -e "  -d, --duration  Seconds"
    
    echo -e "\n${RED}⚠️  WARNING:${NC}"
    echo -e "  • Educational purposes only"
    echo -e "  • Use only on authorized systems"
    echo -e "  • Unauthorized use is illegal"
    
    echo -e "\n${CYAN}══════════════════════════════════════════════════════════════${NC}"
}

# Main installation
main() {
    print_banner
    check_root
    check_python
    check_pip
    check_files
    install_requirements
    make_executable
    add_to_path
    show_usage
    
    echo -e "\n${GREEN}[+] Installation completed!${NC}"
    echo -e "${YELLOW}[*] Run: ./xpro to start${NC}"
}

# Run main
main "$@"
