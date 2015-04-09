import ConfigParser
from __builtin__ import file
import os

from django.http.response import Http404, HttpResponse
from django.shortcuts import render, redirect


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def home(request):
    context = {}
    
    context['selected'] = "view_mac"
    if 'session' in request:
        if 'selected' in request.session:
            context['selected'] = request.session['selected']
            del request.session['selected']
    
    config = ValuesWithCommentsConfigParser()
    config.read(os.path.join(BASE_DIR,'../config.cfg'))

    addressList = dict(config.items('AuthorizedClients'))
    names = {}
    list = []
    
    for key in addressList:
        value = config.get('AuthorizedClients', key)
        if value:
            value = value.split(' ;')
            if value and len(value) == 2:
                address = value[0]
                name = value[1]
                list.append(address)
                names[address] = name
    
    
    context['addresses'] = list
    context['names'] = names
    
    return render(request, 'wifids/mac_addresses.html', context)

def add_mac(request):
    
    if request.method == 'GET':
#         request.session['selected'] = 'add_mac'
        return redirect('home')
    
    if not 'address' in request.POST:
        return Http404()
    if not 'name' in request.POST:
        return Http404()
    
    address = str(request.POST['address'])
    name = str(request.POST['name'])
    print address
    
    config = ValuesWithCommentsConfigParser()
    config.read(os.path.join(BASE_DIR,'../config.cfg'))

    count = 1
    
    f = open(os.path.join(BASE_DIR,'../config.cfg'), 'r')
    wf = open(os.path.join(BASE_DIR,'../_config.cfg'), 'w')
    
    section = False;
    prev_line = ''
    for line in f.readlines():
        if '[AuthorizedClients]' in line:
            section = True
        
        if section and address in line:
            section = False
        
        if section and line == '\n':
            key = prev_line.split(' = ')[0]
            count = key.split('client')
            count = count[1]
            count = int(float(count)) + 1
            new_key = 'client' + str(count)
            new_value = str(address) + ' ;' + str(name)
            new_line = new_key + ' = ' + new_value
            wf.write(new_line)
            wf.write('\n')
            section = False
    
        wf.write(line)
        prev_line = line
            
    f.close()
    wf.close()
    os.rename(os.path.join(BASE_DIR,'../_config.cfg'), os.path.join(BASE_DIR,'../config.cfg'))
    
    return redirect('home')

def delete_mac(request):
    if request.method == 'GET':
        return redirect('home')
    
    if not 'address' in request.POST:
        return Http404()
    
    address = request.POST['address']
    print address
    
    config = ValuesWithCommentsConfigParser()
    config.read(os.path.join(BASE_DIR,'../config.cfg'))

    f = open(os.path.join(BASE_DIR,'../config.cfg'), 'r')
    wf = open(os.path.join(BASE_DIR,'../_config.cfg'), 'w')
    for line in f.readlines():
        if address not in line:
            wf.write(line)
            
    f.close()
    wf.close()
    os.rename(os.path.join(BASE_DIR,'../_config.cfg'), os.path.join(BASE_DIR,'../config.cfg'))
    
    return redirect('home')

def view_log(request):
    context = {}
    context['selected'] = "view_log"
    
    with open (os.path.join(BASE_DIR,'../DEVPLAN.txt'), "r") as f:
        context['log'] = f.read()
    
    
    return render(request, 'wifids/view_logs.html', context);

def view_images(request):
    context = {}
    context['selected'] = "view_images"
    path = '/home/wifids/wifids/images/'
    
    images = os.listdir(path)
    context['gallery'] = []
    
    for image in images:
#         file = path + image
        if image is '.DS_Store':
            continue
        context['gallery'].append(image)
    
    print context['gallery']
#     context['gallery'] = ['http://images.visitcanberra.com.au/images/canberra_hero_image.jpg',
#                           'http://www.hdwallpapersimages.com/wp-content/uploads/2014/01/Winter-Tiger-Wild-Cat-Images.jpg',
#                           'http://www.freelive3dwallpapers.com/wp-content/uploads/2014/03/images-7.jpg',
#                           'http://upload.wikimedia.org/wikipedia/commons/a/a8/VST_images_the_Lagoon_Nebula.jpg',
#                           'http://blog.jimdo.com/wp-content/uploads/2014/01/tree-247122.jpg',
#                           'http://www.desktopwallpaperhd.net/wallpapers/21/7/wallpaper-sunset-images-back-217159.jpg',
#                           'http://img.gettyimageslatam.com/public/userfiles/redesign/images/landing/home/img_entry_002.jpg',
#                           'http://www.wired.com/images_blogs/rawfile/2013/11/offset_WaterHouseMarineImages_62652-2-660x440.jpg',
#                           'http://www.google.com/imgres?imgurl=http://wowslider.com/sliders/demo-22/data1/images/nice_peafowl.jpg&imgrefurl=http://wowslider.com/javascript-slideshow-quiet-rotate-demo.html&h=360&w=960&tbnid=NfygeatVLosRWM:&zoom=1&docid=P6WVaBKnagPTaM&ei=8cgPVfGWLavfsATriYCYCA&tbm=isch&ved=0CEUQMygTMBM'
#                           'http://www.gettyimages.co.uk/gi-resources/images/Homepage/Category-Creative/UK/UK_Creative_462809583.jpg']
    
    return render(request, 'wifids/gallery.html', context);


def get_photo(request, filename):
    context = {}
    context['selected'] = "view_images"
    path = '/home/wifids/wifids/images/'
    
    image = path + filename
    print image
    f = open(os.path.join(BASE_DIR, image), 'r')
    data = f.read()
    f.close()
    
    return HttpResponse(data, content_type=get_content_type(filename))

def get_content_type(filename):
    extension = filename.split('.')
    if len(extension) >= 2:
        extension = extension[len(extension)-1]
    else:
        return 'image/png'
     
    if extension == 'gif':
        return "image/gif"
    elif extension == 'png':
        return 'image/png';
    elif extension == 'jpeg' or filename is 'jpg':
        return 'image/jpeg'

    return 'image/png'

class ValuesWithCommentsConfigParser(ConfigParser.ConfigParser):

    def _read(self, fp, fpname):
        from ConfigParser import DEFAULTSECT, MissingSectionHeaderError, ParsingError

        cursect = None                        # None, or a dictionary
        optname = None
        lineno = 0
        e = None                              # None, or an exception
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno + 1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#;':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                # no leading whitespace
                continue
                # continuation line?
            if line[0].isspace() and cursect is not None and optname:
                value = line.strip()
                if value:
                    cursect[optname].append(value)
            # a section header or option header?
            else:
                # is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if sectname in self._sections:
                        cursect = self._sections[sectname]
                    elif sectname == DEFAULTSECT:
                        cursect = self._defaults
                    else:
                        cursect = self._dict()
                        cursect['__name__'] = sectname
                        self._sections[sectname] = cursect
                        # So sections can't start with a continuation line
                    optname = None
                # no section header in the file?
                elif cursect is None:
                    raise MissingSectionHeaderError(fpname, lineno, line)
                # an option line?
                else:
                    mo = self._optcre.match(line)
                    if mo:
                        optname, vi, optval = mo.group('option', 'vi', 'value')
                        optname = self.optionxform(optname.rstrip())
                        # This check is fine because the OPTCRE cannot
                        # match if it would set optval to None
                        if optval is not None:
                            optval = optval.strip()
                            # allow empty values
                            if optval == '""':
                                optval = ''
                            cursect[optname] = [optval]
                        else:
                            # valueless option handling
                            cursect[optname] = optval
                    else:
                        # a non-fatal parsing error occurred.  set up the
                        # exception but keep going. the exception will be
                        # raised at the end of the file and will contain a
                        # list of all bogus lines
                        if not e:
                            e = ParsingError(fpname)
                        e.append(lineno, repr(line))
            # if any parsing errors occurred, raise an exception
        if e:
            raise e

        # join the multi-line values collected while reading
        all_sections = [self._defaults]
        all_sections.extend(self._sections.values())
        for options in all_sections:
            for name, val in options.items():
                if isinstance(val, list):
                    options[name] = '\n'.join(val)


