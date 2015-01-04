from IPython.terminal.embed import InteractiveShellEmbed
from IPython.config.loader import Config

ipshell = InteractiveShellEmbed(
    config=Config(),
    banner1='Dropping into IPython',
    exit_msg='Leaving Interpreter, back to program.')
