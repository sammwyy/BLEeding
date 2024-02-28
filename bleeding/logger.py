from colorama import Fore

ERR_PREFIX = f"{Fore.RED}ERR   {Fore.RESET}"
WARN_PREFIX = f"{Fore.YELLOW}WARN  {Fore.RESET}"
INFO_PREFIX = f"{Fore.CYAN}INFO  {Fore.RESET}"
HEADLESS = False

def init_logger(headless: bool):
    global HEADLESS
    HEADLESS = headless
    
    if headless:
        global ERR_PREFIX, WARN_PREFIX, INFO_PREFIX
        ERR_PREFIX = "ERR "
        WARN_PREFIX = "WARN "
        INFO_PREFIX = "INFO "
        
def strip_colors(message: str):
    message = message.replace("<black>", "")
    message = message.replace("<blue>", "")
    message = message.replace("<cyan>", "")
    message = message.replace("<green>", "")
    message = message.replace("<magenta>", "")
    message = message.replace("<red>", "")
    message = message.replace("<white>", "")
    message = message.replace("<yellow>", "")
    message = message.replace("<lblack>", "")
    message = message.replace("<lblue>", "")
    message = message.replace("<lcyan>", "")
    message = message.replace("<lgreen>", "")
    message = message.replace("<lmagenta>", "")
    message = message.replace("<lred>", "")
    message = message.replace("<lwhite>", "")
    message = message.replace("<lyellow>", "")
    message = message.replace("<reset>", "")
    return message
        
def format(message: str):
    if HEADLESS:
        return strip_colors(message)
    
    message = message.replace("<black>", Fore.BLACK)
    message = message.replace("<blue>", Fore.BLUE)
    message = message.replace("<cyan>", Fore.CYAN)
    message = message.replace("<green>", Fore.GREEN)
    message = message.replace("<magenta>", Fore.MAGENTA)
    message = message.replace("<red>", Fore.RED)
    message = message.replace("<white>", Fore.WHITE)
    message = message.replace("<yellow>", Fore.YELLOW)
    message = message.replace("<lblack>", Fore.LIGHTBLACK_EX)
    message = message.replace("<lblue>", Fore.LIGHTBLUE_EX)
    message = message.replace("<lcyan>", Fore.LIGHTCYAN_EX)
    message = message.replace("<lgreen>", Fore.LIGHTGREEN_EX)
    message = message.replace("<lmagenta>", Fore.LIGHTMAGENTA_EX)
    message = message.replace("<lred>", Fore.LIGHTRED_EX)
    message = message.replace("<lwhite>", Fore.LIGHTWHITE_EX)
    message = message.replace("<lyellow>", Fore.LIGHTYELLOW_EX)
    message = message.replace("<reset>", Fore.RESET)
    return message
        
def err(message: str):
    if HEADLESS and message == "": return
    print(f"{ERR_PREFIX}{format(message)}")
    
def warn(message: str):
    if HEADLESS and message == "": return
    print(f"{WARN_PREFIX}{format(message)}")
    
def info(message: str): 
    if HEADLESS and message == "": return
    print(f"{INFO_PREFIX}{format(message)}")