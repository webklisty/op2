import subprocess

def main():
    """
    Runs the command "source /home/riopalco/virtualenv/www.riopal.com/bottleshop/2.7/bin/activate && cd /home/riopalco/www.riopal.com/bottleshop".

    Returns:
        None
    """

    subprocess.run(["source", "/home/riopalco/virtualenv/www.riopal.com/bottleshop/2.7/bin/activate", "&&", "cd", "/home/riopalco/www.riopal.com/bottleshop"])

if __name__ == "__main__":
    main()
