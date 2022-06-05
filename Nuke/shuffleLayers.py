#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys
import nuke


def newSelectedNode(channel_list):
    node = nuke.thisNode()
    x = 0

    myversion = nuke.NUKE_VERSION_STRING
    size = len(myversion)
    short_version = myversion[:size - 2]
    version_float = float(short_version)

    for y in channel_list:
      if version_float < 12.1:
        shuffle_node = nuke.createNode("Shuffle")
        shuffle_node['in'].setValue(channel_list[x])
        shuffle_node['label'].setValue("[value in]")
      else:
        shuffle_node = nuke.createNode("Shuffle2")
        shuffle_node['in1'].setValue(channel_list[x])
        shuffle_node['label'].setValue("[value in1]")
      shuffle_node.setInput(0, node)
      x = x+ 1

def mylayerPanel():
    p = nuke.Panel( 'Layer Selection' )
    node = nuke.selectedNode()
    channels = nuke.selectedNode().channels()
    layers = list( [c.split('.') for c in channels])
    only_layer = list(i[0] for i in layers)
    one_layer = list( set(only_layer) )
    mylist = []
    x = 0
    for y in one_layer:
      p.addBooleanCheckBox(one_layer[x], False)
      x = x +1
    p.show()
    t = 0
    for y in one_layer:

      if p.value(one_layer[t]) == True:
          mylist.append(one_layer[t])
      t = t +1
    print("esta lista contiene las capas seleccionadas")
    print(mylist)
    newSelectedNode(mylist)

def selectLayers():
    sel = nuke.thisNode()
    text = nuke.Text_Knob('name', 'Select the layers needed to create shuffle nodes')
    sel.addKnob(text)
    sel.addKnob(nuke.PyScript_Knob('selLayer', "Select your Layers", "{mylayerPanel()}"))


def newNode():
    node = nuke.thisNode()
    channels = nuke.thisNode().channels()
    layers = list( [c.split('.') for c in channels])

    only_layer = list(i[0] for i in layers)
    one_layer = list( set(only_layer) )

    x = 0

    myversion = nuke.NUKE_VERSION_STRING
    size = len(myversion)
    short_version = myversion[:size - 2]
    version_float = float(short_version)

    for y in one_layer:
      if version_float < 12.1:
        shuffle_node = nuke.createNode("Shuffle")
        shuffle_node['in'].setValue(one_layer[x])
        shuffle_node['label'].setValue("[value in]")
      else:
        shuffle_node = nuke.createNode("Shuffle2")
        shuffle_node['in1'].setValue(one_layer[x])
        shuffle_node['label'].setValue("[value in1]")
      shuffle_node.setInput(0, node)

      x = x+ 1

def customShuffle():
    mynode = nuke.thisNode()
    text = nuke.Text_Knob('names', 'Create shuffle nodes from all layers')
    mybutton = nuke.PyScript_Knob('setShuffle', "Create Shuffle nodes", "{newNode()}")
    mynode.addKnob(text)
    mynode.addKnob(mybutton)

nuke.addOnCreate(customShuffle, nodeClass="Read")

nuke.addOnCreate( selectLayers , nodeClass= "Read" )
