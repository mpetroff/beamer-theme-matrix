#!/usr/bin/env python

# generate.py - Generates a Beamer theme matrix
# Copyright (c) 2014 Matthew Petroff
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import subprocess
import tempfile
import os
import shutil

# Options
themes = ['default', 'AnnArbor', 'Antibes', 'Bergen', 'Berkeley', 'Berlin',
    'Boadilla', 'CambridgeUS', 'Copenhagen', 'Darmstadt', 'Dresden',
    'EastLansing', 'Frankfurt', 'Goettingen', 'Hannover', 'Ilmenau',
    'JuanLesPins', 'Luebeck', 'Madrid', 'Malmoe', 'Marburg', 'Montpellier',
    'PaloAlto', 'Pittsburgh', 'Rochester', 'Singapore', 'Szeged', 'Warsaw']
colorThemes = ['default', 'albatross', 'beaver', 'beetle', 'crane', 'dolphin',
    'dove', 'fly', 'lily', 'monarca', 'orchid', 'rose', 'seagull', 'seahorse',
    'spruce', 'whale', 'wolverine']
thumbSize = 200 # Changing thumbnail size requires additonal CSS changes
fullSize = 1000



# Always behave the same no matter where script was called from
scriptDir = os.path.dirname(os.path.realpath(__file__))



#
# Generate LaTeX outputs
#

with open(os.path.join(scriptDir, 'beamer.tex')) as inFile:
    texSource = inFile.read()

outputDir = os.path.join(scriptDir, 'output')
try:
    os.mkdir(outputDir)
except OSError:
    pass    # Directory already exists
os.chdir(outputDir)

tempDir = tempfile.mkdtemp()

# Create PDF for given theme / color combination and optionally copy result
def createPDF(theme, colorTheme, copy=True):
    outFilename = os.path.join(tempDir, theme + '-' + colorTheme + '.tex')
    with open(outFilename, 'w') as outFile:
        out = texSource.replace('#THEME', theme).\
            replace('#COLOR_THEME', colorTheme)
        outFile.write(out)
    
    subprocess.call(['pdflatex', '-output-directory=' + tempDir, outFilename])
    result = outFilename[:-3] + 'pdf'
    if copy:
        shutil.copy(result, colorTheme + '.pdf')
    return colorTheme + '.pdf'

# Create PNG from PDF
def createImage(pdf, prefix, width):
    subprocess.call(['pdftoppm', '-scale-to', str(width), '-png', pdf, prefix])

# First LaTeX run
createPDF('default', 'default', False)

# Create samples
for theme in themes:
    themeDir = os.path.join(outputDir, theme)
    try:
        os.mkdir(themeDir)
    except OSError:
        pass    # Directory already exists
    os.chdir(themeDir)
    thumbs = []
    for colorTheme in colorThemes:
        pdf = createPDF(theme, colorTheme)
        createImage(pdf, pdf[:-4] + '-thumb', thumbSize)
        createImage(pdf, pdf[:-4] + '-full', fullSize)
        thumbs.append(pdf[:-4] + '-thumb-1.png')
        thumbs.append(pdf[:-4] + '-thumb-2.png')
        os.remove(pdf)  # Clean up
    subprocess.call(['convert'] + thumbs + ['+append', 'thumbs.png'])
    subprocess.call(['pngquant', '-f', '--ext', '.png', 'thumbs.png'])
    
    # Clean up
    for thumb in thumbs:
        os.remove(thumb)
    
    # Optimize
    subprocess.call('optipng *.png', shell=True)



#
# Create web page
#

htmlTable = '<table class="theme-grid">'
for theme in themes:
    htmlTable += '<tr>'
    for i in range(len(colorThemes)):
        colorTheme = colorThemes[i]
        htmlTable += '<td><div class="iblock"><div class="table">' \
            + '<div class="table-row"><div class="table-cell">' \
            + '<a href="' + theme + '/' + colorTheme \
            + '-full-1.png" data-sbox=' + theme + colorTheme \
            + ' title="Theme: ' + theme + ', Color Theme: ' \
            + colorTheme + '">' \
            + '<div class="beamer-thumb" style="background: url(\'' + theme \
            + '/thumbs.png\') -' + str(i * 2 * thumbSize) \
            + 'px 0;"></div></a></div><div class="table-cell">' \
            + '<a href="' + theme + '/' + colorTheme \
            + '-full-2.png" data-sbox=' + theme + colorTheme \
            + ' title="Theme: ' + theme + ', Color Theme: ' + colorTheme \
            + '"><div class="beamer-thumb beamer-right" ' \
            + 'style="background: url(\'' + theme + '/thumbs.png\') -' \
            + str((i * 2 + 1) * thumbSize) \
            + 'px 0;"></div></a></div></div></div></div></td>\n'
    htmlTable += '</tr>'
htmlTable += '</table>'

topHeader = ''
for colorTheme in colorThemes:
    topHeader += '<td>' + colorTheme + '</td>\n'
leftHeader = ''
for theme in themes:
    leftHeader += '<tr><td><div>' + theme + '</div></td></tr>\n'

os.chdir(outputDir)
with open(os.path.join(scriptDir, 'matrix.html')) as inFile:
    htmlSource = inFile.read()
with open('index.html', 'w') as outFile:
    out = htmlSource.replace('#TABLE', htmlTable).\
        replace('#TOP_HEADER', topHeader).replace('#LEFT_HEADER', leftHeader)
    outFile.write(out)

with open(os.path.join(scriptDir, 'style.css')) as inFile:
    cssSource = inFile.read()
with open('style.css', 'w') as outFile:
    out = cssSource.replace('#TABLE_WIDTH', str(425 * len(colorThemes)) + 'px')
    outFile.write(out)

includesDir = os.path.join(scriptDir, 'includes')
shutil.copy(os.path.join(includesDir, 'bootstrap.min.css'), '.')
shutil.copy(os.path.join(includesDir, 'slenderbox.css'), '.')
shutil.copy(os.path.join(includesDir, 'slenderbox.js'), '.')
