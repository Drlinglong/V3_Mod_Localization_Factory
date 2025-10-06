# scripts/utils/banner.py

def print_banner():
    """
    Prints the new, large, truecolor "Remis" banner with precise brand colors.
    """
    # Hex: #702963 -> RGB: (112, 41, 99)
    PURPLE = '\033[38;2;112;41;99m'
    # Hex: #FFCC00 -> RGB: (255, 204, 0)
    GOLD = '\033[93m' # Using bright yellow as a strong and compatible gold
    RESET = '\033[0m'
    # Much larger ASCII art for "REMIS" with 9-line character height
    banner = f"""
{RESET}===========================================================================
 {GOLD}███████████      {RESET}{PURPLE}██████████   {PURPLE}██████  {PURPLE}██████    {PURPLE} █████     {PURPLE}█████████{RESET}
{GOLD}▒▒███▒▒▒▒▒███    {RESET}{PURPLE}▒███▒▒▒▒▒█   {PURPLE}▒▒██████{PURPLE}███████    {PURPLE}▒▒███     {PURPLE}███▒▒▒▒▒███{RESET}
 {GOLD}▒███    ▒███     {RESET}{PURPLE}▒███  █ ▒    {PURPLE}▒███▒█████▒███     {PURPLE}▒███    {PURPLE}▒███    ▒▒▒{RESET}
 {GOLD}▒██████████      {RESET}{PURPLE}▒██████      {PURPLE}▒███▒▒███ ▒███     {PURPLE}▒███    {PURPLE}▒▒█████████{RESET}
 {GOLD}▒███▒▒▒▒▒███     {RESET}{PURPLE}▒███▒▒█      {PURPLE}▒███ ▒▒▒  ▒███     {PURPLE}▒███     {PURPLE}▒▒▒▒▒▒▒▒███{RESET}
 {GOLD}▒███    ▒███     {RESET}{PURPLE}▒███ ▒   █   {PURPLE}▒███      ▒███     {PURPLE}▒███     {PURPLE}███    ▒███{RESET}
 {GOLD}█████   █████    {RESET}{PURPLE}██████████   {PURPLE}█████     █████    {PURPLE}█████   {PURPLE}▒▒█████████{RESET}
 {GOLD}▒▒▒▒▒   ▒▒▒▒▒    {RESET}{PURPLE}▒▒▒▒▒▒▒▒▒▒   {PURPLE}▒▒▒▒▒     ▒▒▒▒▒    {PURPLE}▒▒▒▒▒     {PURPLE}▒▒▒▒▒▒▒▒▒{RESET}
{RESET}                                                                                                                            {RESET}
{RESET}          P社Mod本地化工厂 (Paradox Mod Localization Factory){RESET}
{RESET}===========================================================================
    """
    print(banner)