#!/bin/env python3

"""
==PSST (PYTHON STATIC SITE TOOL)==

MIT License

Copyright (c) 2023 Henderson Reed Hummel & Lucas Elijah Friedman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import os
import shutil
import subprocess
import http.server
import socketserver
import pathlib


help = """
usage: psg [command]

commands:
    build - converts the site source stored in the `src` directory, and places it in the `docs` directory.
    serve - builds the the docs directory and launches Python's builtin server to serve the docs directory.
    clean - deletes the docs directory.
    help - display this message.

psg depends on the existence of the following:
    - `pandoc` in your $PATH
    - template.html, into which our page html is injected
    - a "src" directory containing the website to be generated.
"""  # noqa

valid_commands = ["build", "serve", "clean", "help"]

# Check if there is at least one argument,
# setting it to `command` for future reference.
if (len(sys.argv) < 2 or
   sys.argv[1] == "help" or
   sys.argv[1] not in valid_commands):
    print(help)
    sys.exit(1)

command = sys.argv[1]

# checking for required files/directories.
if not os.path.isfile("template.html"):
    print("template.html does not exist. Exiting now.")
    sys.exit(1)
else:
    with open("template.html", "r") as file:
        template_html = file.read()
        header_html, footer_html = template_html.split("$content$")

if not os.path.isdir("src"):
    print("src directory does not exist. Exiting now.")
    sys.exit(1)


def preprocess(src, dest):
    """
    adds the header and footer html around the page
    """
    # print(f"would have converted {src}")
    # shutil.copy(src, dest)
    with open(src, "r") as file:
        src_html = file.read()
        out_html = (header_html + "\n" +
                  src_html + "\n" +
                  footer_html)

    with open(dest, "w") as file:
        file.write(out_html)


def build():
    """
    - find the `src` dir
    - iterate through every file in it.
    - run the case statement on the file extension:
        if html, process (add header and footer) and copy.
        if not md, just copy
    """
    source_directory = "src"
    destination_directory = "docs"
    os.makedirs(destination_directory, exist_ok=True)

    for root, dirs, files in os.walk(source_directory):
        for directory in dirs:
            current_dir = os.path.join(root, directory)
            dest_dir = os.path.join(
                    destination_directory,
                    os.path.relpath(current_dir, source_directory))
            os.makedirs(dest_dir, exist_ok=True)

        for file in files:
            source_path = os.path.join(root, file)
            dest_path = os.path.join(
                    destination_directory,
                    os.path.relpath(source_path, source_directory))

            if file.endswith(".html"):
                # Handle HTML files differently
                preprocess(source_path, dest_path)
            else:
                # Copy non-HTML files
                shutil.copy(source_path, dest_path)


def serve():
    """
    calls `build`,
    and calls the python http server to serve the `docs` dir.
    """
    build()

    os.chdir('./docs/')

    handler = http.server.SimpleHTTPRequestHandler
    port = 8080
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving directory at http://localhost:{port}")
        httpd.serve_forever()


def clean():
    """
    simply deletes the docs directory.
    """
    shutil.rmtree("./docs/")


eval(f"{command}()")