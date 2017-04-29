import Tkinter as tk
from urlparse import urlparse
import webbrowser
from urllib import quote_plus

debugoutput = False
links = []
linkcount = 0
lastsender = ""
systemlinks = []
systemcount = 0

idx = ''

thisevent = ''
tag_to_handle = ''

from datetime import datetime
import time

def on_click(event, widget_origin='?'):
    global tag_to_handle
    if tag_to_handle:
        if tag_to_handle == "systemlink":
          systempopup(event)
        elif tag_to_handle =="link":
          linkpopup(event)
        tag_to_handle = ''
    else:
        popup(event)

def on_tag_click(event, tag):
    global tag_to_handle
    tag_to_handle = tag

def datetime_from_utc_to_local(utc_datetime):
  now_timestamp = time.time()
  offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
  return utc_datetime + offset

def copy_button3(event=''):
  try:
    setclipboard(plugin_app.status.selection_get())
  except:
    pass

def setclipboard(text):
  r = tk.Tk()
  r.clipboard_clear()
  r.clipboard_append(text)
  r.destroy()

def plugin_start():
  """
  Load this plugin into EDMC
  """
  print "Chat Viewer started"
  return "Chat Viewer"

def showLink(event):
    idx = int(event.widget.tag_names(tk.CURRENT)[1])
    webbrowser.open(links[idx])

def copyLink(event=''):
    setclipboard(links[idx])

def showSystem(event):
    idx = int(event.widget.tag_names(tk.CURRENT)[1])
    webbrowser.open("https://www.edsm.net/show-system?systemName=" + quote_plus(systemlinks[idx]))

def copySystem(event=''):
    setclipboard(systemlinks[idx])

def copySystemLink(event=''):
    setclipboard("https://www.edsm.net/show-system?systemName=" + quote_plus(systemlinks[idx]))

def systempopup(event):
    global idx
    idx = int(event.widget.tag_names(tk.CURRENT)[1])
    plugin_app.systemMenu.post(event.x_root, event.y_root)

def linkpopup(event):
    global idx
    idx = int(event.widget.tag_names(tk.CURRENT)[1])
    plugin_app.linkMenu.post(event.x_root, event.y_root)

def popup(event):
    plugin_app.menu.post(event.x_root, event.y_root)

def plugin_app(parent):
  """
  Create a TK widget for the EDMC main window
  """
  plugin_app.frame = tk.Frame(parent)
  plugin_app.status = tk.Text(plugin_app.frame)
  plugin_app.chatcopy = tk.Button(plugin_app.frame, text = "Copy", command = copy_button3)
  plugin_app.chatcopy.grid(row = 1, column = 0, columnspan = 4)
  plugin_app.status['width'] = 27
  plugin_app.status.grid(row=0, column = 0, columnspan = 3)
  plugin_app.status.insert(tk.END,"Chat Viewer loaded")
  plugin_app.status.config(state=tk.DISABLED)
  plugin_app.status.config(height=10, wrap='word')
  plugin_app.status.see(tk.END)
  plugin_app.status.bind('<Button-3>', lambda e, w='textwidget': on_click(e, w))
  plugin_app.status.bind('Control-x', copy_button3)
  plugin_app.status.tag_config('link', underline=1)
  plugin_app.status.tag_bind('link', '<Button-1>', showLink)
  plugin_app.status.tag_bind('link', '<Button-3>', lambda e, w='link': on_tag_click(e, w))
  plugin_app.status.tag_config('systemlink', underline=1)
  plugin_app.status.tag_bind('systemlink', '<Button-1>', showSystem)
  plugin_app.status.tag_bind('systemlink', '<Button-3>', lambda e, w='systemlink': on_tag_click(e, w))
  plugin_app.freeze = tk.IntVar(plugin_app.frame)
  plugin_app.freezebutton = tk.Checkbutton(plugin_app.frame, text="Freeze", variable = plugin_app.freeze)
  plugin_app.freezebutton.grid(row=2, column = 0, columnspan = 4)
  plugin_app.scroll = tk.Scrollbar(plugin_app.frame, command=plugin_app.status.yview)
  plugin_app.scroll.grid(row=0, column=4, sticky='nsew')
  plugin_app.status['yscrollcommand'] = plugin_app.scroll.set
  plugin_app.systemMenu = tk.Menu(plugin_app.frame, tearoff=0)
  plugin_app.systemMenu.add_command(label="Copy system name", command = copySystem)
  plugin_app.systemMenu.add_command(label="Copy EDSM link", command = copySystemLink)
  plugin_app.menu = tk.Menu(plugin_app.frame, tearoff=0)
  plugin_app.menu.add_command(label="Copy text (Ctrl x)", command = copy_button3)
  plugin_app.linkMenu = tk.Menu(plugin_app.frame, tearoff=0)
  plugin_app.linkMenu.add_command(label="Copy link", command = copyLink)
  print "Chat Viewer loaded"
  return (plugin_app.frame)

def journal_entry(cmdr, system, station, entry):
  global links
  global linkcount
  global systemlinks
  global systemcount
  global lastsender
  eventtimestamp = datetime.strptime(entry["timestamp"], '%Y-%m-%dT%H:%M:%SZ')
  localeventtime = datetime_from_utc_to_local(eventtimestamp)
  localtimestamp = localeventtime.strftime('%H:%M')
  if debugoutput == True:
    plugin_app.status.config(state=tk.NORMAL)
    plugin_app.status.insert(tk.END, "\n{}".format(entry))
    plugin_app.status.see(tk.END)
    plugin_app.status.config(state=tk.DISABLED)
  event = entry["event"]
  display = False
  if event == "SendText":
    sender = cmdr
    display = True
    channel = entry['To'][0]
  elif event == "ReceiveText":
    sender = entry["From"]
    if sender[:21] == "$cmdr_decorate:#name=":
      sender = sender[21:-1]
      channel = entry["Channel"][0]
      display = True
  elif event == "FSDJump" or event == "StartJump":
    formtext = {"FSDJump": "Arrived at",
                "StartJump": "Jumping to",
                }
    try:
      systemlinks.append(entry["StarSystem"])
      plugin_app.status.config(state=tk.NORMAL)
      plugin_app.status.insert(tk.END, "\n[{}] * {} ".format(localtimestamp,formtext[event]))
      plugin_app.status.insert(tk.END, "{}".format(entry["StarSystem"]), ('systemlink', systemcount))
      plugin_app.status.insert(tk.END, " *")
      systemcount = systemcount + 1
      if plugin_app.freeze.get() != 1:
        plugin_app.status.see(tk.END)
      plugin_app.status.config(state=tk.DISABLED)
      if lastsender != cmdr:
        lastsender = ''
    except:
      pass
  if display == True:
    plugin_app.status.config(state=tk.NORMAL)
    if sender != lastsender:
      plugin_app.status.insert(tk.END, "\nCMDR {}:".format(sender))
    plugin_app.status.insert(tk.END, "\n[{}][{}] ".format(localtimestamp, channel.upper()))
    for word in entry["Message"].split(' '):
      thing = urlparse(word.strip())
      if thing.scheme:
        links.append(word)
        plugin_app.status.insert(tk.END, "{} ".format(word), ('link', linkcount))
        linkcount = linkcount + 1
      else:
        plugin_app.status.insert(tk.END, "{} ".format(word))
    if plugin_app.freeze.get() != 1:
      plugin_app.status.see(tk.END)
    plugin_app.status.config(state=tk.DISABLED)
    lastsender = sender