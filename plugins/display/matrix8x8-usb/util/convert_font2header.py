#!/usr/bin/env python
# Processing file with binary pixel fonts
# Limitation: fixed height, byte symbols, limited height & width to 8
#  Format:
# <symbol> <first bin line>,<second bin line>,...
#  Example:
# ...
# / 0001,0010,0100,1000,0000
# 0 010,101,101,010,000
# ...

import sys, os
from math import ceil

for f in sys.argv[1:]:
    if not os.path.isfile(sys.argv[1]):
        print "ERROR: skipping non-file %s" % f
        continue

    name = f.rsplit('.', 1)[0]

    print "Processing font file '%s':" % f
    font = { 'data':{} }
    error = False

    with open(f, 'r') as fd:
        for line in fd:
            line = line.rstrip()

            pic = line[2:].split(',')
            height = len(pic)
            width = len(pic[0])

            if not width in font['data']:
                font['data'][width] = {}

            if 'height' in font:
                if font['height'] != height:
                    error = True
                    print "  ERROR: height of pic for symbol '%s' (%d) is differs from the first pic height (%d)" % (line[0], height, font['height'])
            else:
                font['height'] = height

            # Check width of each pic line
            for l in pic:
                if len(l) != width:
                    error = True
                    print "  ERROR: width of pic line '%s' of symbol '%s' is differs from the first pic line (%d)" % (l, line[0], width)
                if len([ True for c in l if c not in ['0', '1'] ]) > 0:
                    error = True
                    print "  ERROR: found wrong (nor '0' or '1') symbol in the line '%s' of symbol '%s'" % (l, line[0])

            # Position will be calculated later
            font['data'][width][ord(line[0])] = pic

    if error:
        print "  Errors found while parsing of the file '%s'. Please, check & fix errors in the font file." % f
        continue

    # Place all data into one-level char array
    # Each symbol width - begins with a new char
    font['bytes'] = []
    font['symbols'] = {}
    font['offset'] = {}
    for width in font['data']:
        font['symbols'][width] = sorted(font['data'][width])
        tmpbytes = ''
        for symbol_ord in font['symbols'][width]:
            data = font['data'][width][symbol_ord]
            print "  Processing:", width, chr(symbol_ord), symbol_ord, data
            tmpbytes += ''.join(data)

        font['offset'][width] = len(font['bytes'])

        for i in range(int(ceil(len(tmpbytes)/8.0))):
            font['bytes'].append('0x%02x' % int(tmpbytes[i*8:i*8+8].ljust(8, '0'), 2))

    with open(name + ".generated.h", 'w') as fdw:
        data_chars = [ chr(char) for char in range(ord('0'),ord('9')+1) + range(ord('a'),ord('z')+1) ]
        data_name = os.path.basename(name)
        data_name = ''.join([ c if c in data_chars else '_' for c in data_name ])
        guard_name = data_name.upper() + '_H'

        fdw.write("#ifndef %s\n" % guard_name)
        fdw.write("#define %s\n" % guard_name)
        fdw.write("// Font data for %s\n" % f)

        fdw.write('\nconst uint8_t %s_data[%d] PROGMEM = {\n' % (data_name, len(font['bytes'])))
        print(font)
        for i in range(int(ceil(len(font['bytes'])/8.0))):
            fdw.write('    %s,\n' % ','.join(font['bytes'][i*8:i*8+8]))
        fdw.write("};\n\n")

        fdw.write('#define %s_HEIGHT %d\n\n' % (data_name.upper(), font['height']))

        for w in font['symbols']:
            fdw.write('const char %s_width_%d[] = "%s";\n' % (data_name, w, ''.join([ '\\x%02x' % o for o in font['symbols'][w] ])))

        fdw.write("\nuint8_t getCharWidth%s(uint8_t ascii) {\n" % data_name.capitalize())
        fdw.write("    char *pch;\n\n")
        for w in font['symbols']:
            fdw.write("    pch = strchr(%s_width_%d, ascii);\n" % (data_name, w))
            fdw.write("    if( pch != NULL ) { return %d; }\n\n" % w)
        fdw.write("    return 0;\n")
        fdw.write("}\n")

        fdw.write("\nuint8_t getCharPos%s(uint8_t ascii, uint16_t *pos, uint16_t *offset) {\n" % data_name.capitalize())
        fdw.write("    char *pch;\n\n")
        for w in font['symbols']:
            fdw.write("    pch = strchr(%s_width_%d, ascii);\n" % (data_name, w))
            fdw.write("    if( pch != NULL ) { *pos = (pch - %s_width_%d)*%s_HEIGHT*%d; *offset = %d; return %d; }\n\n" % (data_name, w, data_name.upper(), w, font['offset'][w], w))
        fdw.write("    return 0;\n")
        fdw.write("}\n")

        fdw.write("\n#endif // %s\n" % guard_name)

