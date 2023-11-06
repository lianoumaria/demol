#!/usr/bin/env python

"""
hw_conns_plantuml.py
Script that generates PlantUML text from textX models
"""

# PlantUML generation for connection model
def device_to_plantuml(model):
    filename = f'my_{model.metadata.name}.pu'
    f = open(filename, "w")

    tmp = '@startuml\n' + \
        '\nskinparam componentStyle rectangle' + \
        '\nskinparam linetype ortho' + \
        '\nskinparam NoteFontSize 15' + \
        '\nskinparam NoteFontStyle italics' + \
        '\nskinparam RectangleFontSize 16\n' + \
        '\n!define T2 \\t\\t' + \
        '\n!define T3 \\t\\t\\t' + \
        '\n!define T5 \\t\\t\\t\\t\\t' + \
        '\n!define NL2 \\n\\n' + \
        '\n!define NL4 \\n\\n\\n\\n'  + \
        '\n!define NL6 \\n\\n\\n\\n\\n\\n' + \
        '\n!define NL10 \\n\\n\\n\\n\\n\\n\\n\\n\\n\\n' + \
        '\n\n'
    f.write(tmp)

    tmp = 'component [NL10 T3 **' + str(model.connections[0].board.name) + \
        '** T3 NL10] as ' + str(model.connections[0].board.name) + ' #FFF9C2\n'
    f.write(tmp)

    for i in range(len(model.connections)):
        tmp = 'component [' + (i%4 < 2)*'NL4 T2' + (i%4 >= 2)*'NL2 T5' + \
            ' **' + str(model.connections[i].peripheral.name) + \
            '** ' +  (i%4 < 2)*'T2 NL4' + (i%4 >= 2)*'T5 NL2' + \
            '] as ' + str(model.connections[i].peripheral.name) + \
            ' #CAE2C8\n'
        f.write(tmp)
    f.write('\n')

    note_directions = ['top', 'bottom', 'right', 'left']
    for i in range(len(model.connections)):
        tmp = 'note ' + note_directions[i%4] + ' of ' + \
            str(model.connections[i].peripheral.name) + \
            ' : topic - "' + str(model.connections[i].endpoint.topic[:-1]) + '"\n'
        f.write(tmp)
    f.write('\n')

    directions = ['left', 'right', 'up', 'down']
    for i in range(len(model.connections)):
        tmp = f'{model.connections[i].board.name} ' + \
            f'..{directions[i%len(directions)]}.. {model.connections[i].peripheral.name}\n'
        for j in range(len(model.connections[i].ioConns)):
            if model.connections[i].ioConns[j].type == 'gpio':
                tmp += str(model.connections[i].board.name) + \
                    ' "**' + str(model.connections[i].ioConns[j].pinConn.peripheralPin) + \
                    '**" #----# "**' + \
                    str(model.connections[i].ioConns[j].pinConn.boardPin) + \
                    '**" ' + str(model.connections[i].peripheral.name) + \
                    (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            elif model.connections[i].ioConns[j].type == 'i2c':
                tmp += str(model.connections[i].board.name) + \
                    ' "**' + \
                    str(model.connections[i].ioConns[j].sda.peripheralPin) + \
                    '**" #----# "**' + \
                    str(model.connections[i].ioConns[j].sda.boardPin) + \
                    '**" ' + str(model.connections[i].peripheral.name) + \
                    (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
                tmp += str(model.connections[i].board.name) + \
                    ' "**' + \
                    str(model.connections[i].ioConns[j].scl.peripheralPin) + \
                    '**" #----# "**' + \
                    str(model.connections[i].ioConns[j].scl.boardPin) + \
                    '**" ' + str(model.connections[i].peripheral.name) + \
                    (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
        f.write(tmp)

        for j in range(len(model.connections[i].powerConns)):
            tmp = str(model.connections[i].board.name) + \
                ' "**' + str(model.connections[i].powerConns[j].peripheralPin) + \
                '**" #----# "**' + \
                str(model.connections[i].powerConns[j].boardPin) + \
                '**" ' + str(model.connections[i].peripheral.name) + \
                (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            f.write(tmp)

        f.write('\n')

    f.write('\nhide @unlinked\n@enduml')

    f.close()