#!/usr/bin/env python
# Script to convert RGB ppm animation frames into a header file with data

import sys, os

for d in sys.argv[1:]:
    ppms = [ f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f)) and f.endswith(".ppm") ]
    if len(ppms) < 1:
        raise Exception("ERROR: unable to find ppm files in directory '%s'" % d)

    with open(d + ".h", 'w') as fdw:
        guard_name = d.upper() + '_H'
        fdw.write("#ifndef %s\n" % guard_name)
        fdw.write("#define %s\n\n" % guard_name)
        fdw.write("// %s frames\n" % d)
        fdw.write("uint8_t frames_%s[%d][3][64] = {\n" % (d, len(ppms)))
        ppms.sort()
        for f in ppms:
            with open(os.path.join(d, f), 'rb') as fd:
                if fd.readline().strip() != 'P6':
                    raise Exception("ERROR: not a PPM file: '%s'" % os.path.join(d, f))

                fdw.write("  { // %s\n" % f)
                data = []
                for line in fd:
                    if line[0] != "#":
                        data.append(line)

                size = map(int, data[0].strip().split(" "))

                matrix = [[],[],[]]
                for x in range(size[0]):
                    line = [[],[],[]]
                    for y in range(size[1]):
                        offset = (x*size[1]*3)+(y*3)
                        for c in (0,1,2):
                            line[c].append('0x%02x' % ord(data[2][offset+c]))
                    for c in (0,1,2):
                        matrix[c].append(line[c])
                
                for c in matrix:
                    fdw.write("    {\n")
                    for l in c:
                        fdw.write("      %s,\n" % ','.join(l))
                    fdw.write("    },\n")

                fdw.write("  }, // end %s\n" % f)
        fdw.write("};\n")
        fdw.write("\n#endif // %s\n" % guard_name)
