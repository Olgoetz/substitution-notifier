from lib.commands import main
from pyfiglet import Figlet

if __name__ == "__main__":
    f = Figlet(font='slant')
    print(f.renderText('Substitutor Notifier CLI'))
    main()