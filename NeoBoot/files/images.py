# -*- coding: utf-8 -*-
#from __future__ import print_function
from Plugins.Extensions.NeoBoot.__init__ import _
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Sources.List import List
from Components.PluginList import resolveFilename
from Components.Task import Task, Job, job_manager, Condition
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.TaskView import JobView
from Tools.Downloader import downloadWithProgress
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, SCOPE_PLUGINS
import urllib2
import os
import shutil
import math
from Plugins.Extensions.NeoBoot.files.stbbranding import getBoxType, getMachineBuild, getTypBoxa

class ChooseOnLineImage(Screen):
    skin = """
    <screen name="ChooseOnLineImage" position="center,center" size="880,620" title="%s" >
        <widget source="list" render="Listbox" position="10,0" size="870,610" scrollbarMode="showOnDemand" transparent="1">
            <convert type="TemplatedMultiContent">
                {"template": [
                    MultiContentEntryText(pos = (0, 10), size = (830, 30), font=0, flags = RT_HALIGN_RIGHT, text = 0),
                    MultiContentEntryPixmapAlphaBlend(pos = (10, 0), size = (480, 60), png = 1),
                    MultiContentEntryText(pos = (0, 40), size = (830, 30), font=1, flags = RT_VALIGN_TOP | RT_HALIGN_RIGHT, text = 3),
                    ],
                    "fonts": [gFont("Regular", 28),gFont("Regular", 20)],
                    "itemHeight": 65
                }
            </convert>
        </widget>
    </screen>""" % (_('NeoBoot - Download OnLine Images'))

    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self.updateList()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.KeyOk,
         'back': self.close})

    def KeyOk(self):
        self.sel = self['list'].getCurrent()
        returnValue = self.sel[2]
        if returnValue is not None:
            self.session.openWithCallback(self.quit, DownloadOnLineImage, returnValue)
        return

    def updateList(self):
        self.list = []
        mypath = resolveFilename(SCOPE_PLUGINS)
        mypath = mypath + 'Extensions/NeoBoot/software/png/'
        mypixmap = mypath + 'openatv.png'
        png = LoadPixmap(mypixmap)
        name = _('OpenATV-6.0')
        desc = _('Download latest OpenATV Image')
        idx = 'openatv'
        res = (name,
         png,
         idx,
         desc)
        self.list.append(res)
        mypixmap = mypath + 'openpli.png'
        png = LoadPixmap(mypixmap)
        name = _('OpenPLi')
        desc = _('Download latest OpenPLi Image')
        idx = 'openpli'
        res = (name,
         png,
         idx,
         desc)
        self.list.append(res)
        mypixmap = mypath + 'openvix.png'
        png = LoadPixmap(mypixmap)
        name = _('OpenVIX')
        desc = _('Download latest OpenVIX Image')
        idx = 'openvix'
        res = (name,
         png,
         idx,
         desc)
        self.list.append(res)
        self['list'].list = self.list

    def quit(self):
        self.close()


class DownloadOnLineImage(Screen):
    skin = '\n\t<screen position="center,center" size="560,500" title="NeoBoot - Download Image">\n\t\t<ePixmap position="0,460"   zPosition="1" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t<ePixmap position="140,460" zPosition="1" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t<widget name="key_red" position="0,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t<widget name="key_green" position="140,460" zPosition="2" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t<widget name="imageList" position="10,10" zPosition="1" size="550,450" font="Regular;20" scrollbarMode="showOnDemand" transparent="1" />\n\t</screen>'

    def __init__(self, session, distro):
        Screen.__init__(self, session)
        self.session = session
        Screen.setTitle(self, _('NeoBoot - Download Image'))
        self['key_green'] = Button(_('Install'))
        self['key_red'] = Button(_('Exit'))
        self.filename = None
        self.imagelist = []
        self.simulate = False
        self.imagePath = '/media/neoboot/ImagesUpload'
        self.distro = distro
        if self.distro == 'openatv':
            self.feed = 'openatv'
            self.feedurl = 'http://images.mynonpublic.com/openatv/6.0'
        elif self.distro == 'openpli':
            self.feed = 'openpli'
            self.feedurl = 'http://openpli.org/download'
        elif self.distro == 'openvix':
            self.feed = 'openvix'
            self.feedurl = 'http://www.openvix.co.uk'
        elif self.distro == 'opendroid':
            self.feed = 'opendroid'
            self.feedurl = 'http://images.opendroid.org/5.5/'
        else:
            self.close()
        self['imageList'] = MenuList(self.imagelist)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'green': self.green,
         'red': self.quit,
         'cancel': self.quit}, -2)
        self.onLayoutFinish.append(self.layoutFinished)
        return

    def quit(self):
        self.close()

    def box(self):
        box = getBoxType()
        urlbox = getBoxType()
        if self.distro == 'openatv':
            if box in ('xpeedlx1', 'xpeedlx2'):
                box = 'xpeedlx'
            req = urllib2.Request(self.feedurl)
            stb = 'no Image for this Box on this Side'
            try:
                response = urllib2.urlopen(req)
                tmp = response.readlines()
                for line in tmp:
                    if '<a href="' in line:
                        if box in line:
                            stb = '1'
                            break

            except:
                stb = 'no Image for this Box on this Side'

        if self.distro == 'openvix':
            if box in ('xpeedlx1', 'xpeedlx2', 'xpeedlx3', 'uniboxhd1', 'uniboxhd2', 'uniboxhd3', 'vusolo2', 'vusolose', 'vuultimo', 'vuuno', 'vuduo2', 'vuduo', 'sf8', 'mutant2400', 'gbquad', 'gbquadplus', 'gb800ueplus', 'gb800seplus', 'gb800se'):
                if box in 'vusolo2':
                    box = 'vusolo2'
                    urlbox = 'Vu%2BSolo2'
                    stb = '1'
                elif box in 'vusolose':
                    box = 'vusolose'
                    urlbox = 'Vu%2BSolose'
                    stb = '1'
                elif box in 'vuultimo':
                    box = 'vuultimo'
                    urlbox = 'VuUltimo'
                    stb = '1'
                elif box in 'vuuno':
                    box = 'vuuno'
                    urlbox = 'Vu%2BUno'
                    stb = '1'
                elif box in 'vuduo2':
                    box = 'vuduo2'
                    urlbox = 'Vu%2BDuo2'
                    stb = '1'
                elif box in 'vuduo':
                    box = 'vuduo'
                    urlbox = 'Vu%2BDuo'
                    stb = '1'
                elif box in 'mutant2400':
                    box = 'mutant2400'
                    urlbox = 'Mutant-HD2400'
                    stb = '1'
                elif box in 'gbquad':
                    box = 'gbquad'
                    urlbox = 'GiGaBlue-HD-QUAD'
                    stb = '1'
                elif box in 'gbquadplus':
                    box = 'gbquadplus'
                    urlbox = 'GiGaBlue-HD-QUAD-PLUS'
                    stb = '1'
                elif box in 'gb800se':
                    box = 'gb800se'
                    urlbox = 'GiGaBlue-HD800SE'
                    stb = '1'
                elif box in 'gb800ueplus':
                    box = 'gb800ueplus'
                    urlbox = 'GiGaBlue-HD800UE-PLUS'
                    stb = '1'
                elif box in 'gb800seplus':
                    box = 'gb800seplus'
                    urlbox = 'GiGaBlue-HD800SE-PLUS'
                    stb = '1'
            else:
                stb = 'no Image for this Box on this Side'
        elif self.distro == 'openpli':
            if box in ('vusolo2', 'vusolose', 'vuultimo', 'vuuno', 'vuduo2', 'vuduo', 'mutant2400', 'quadbox2400', 'xp1000', 'formuler1', 'formuler3'):
                if box in 'vusolo2':
                    box = 'vusolo2'
                    urlbox = 'vuplus/vusolo2/'
                    stb = '1'
                if box in 'vusolose':
                    box = 'vusolose'
                    urlbox = 'vuplus/vusolose/'
                    stb = '1'
                elif box in 'vuultimo':
                    box = 'vuultimo'
                    urlbox = 'vuplus/vuultimo/'
                    stb = '1'
                elif box in 'vuuno':
                    box = 'vuuno'
                    urlbox = 'vuplus/vuuno/'
                    stb = '1'
                elif box in 'vuduo2':
                    box = 'vuduo2'
                    urlbox = 'vuplus/vuduo2/'
                    stb = '1'
                elif box in 'vuduo':
                    box = 'vuduo'
                    urlbox = 'vuplus/vuduo/'
                    stb = '1'
            else:
                stb = 'no Image for this Box on this Side'
        return (box, urlbox, stb)

    def green(self, ret = None):
        sel = self['imageList'].l.getCurrentSelection()
        if sel == None:
            print 'Nothing to select !!'
            return
        else:
            file_name = self.imagePath + '/' + sel
            self.filename = file_name
            self.sel = sel
            box = self.box()
            self.hide()
            if self.distro == 'openvix':
                typboxa = getTypBoxa()
                url = self.feedurl + '/openvix-builds/' + typboxa + '/' + sel
            elif self.distro == 'openpli':
                url = 'http://downloads.pli-images.org/builds/' + box[0] + '/' + sel
            print '[NeoBoot] Image download url: ', url
            try:
                u = urllib2.urlopen(url)
            except:
                self.session.open(MessageBox, _('The URL to this image is not correct !!'), type=MessageBox.TYPE_ERROR)
                self.close()

            f = open(file_name, 'wb')
            f.close()
            meta = u.info()
            file_size = int(meta.getheaders('Content-Length')[0])
            print 'Downloading: %s Bytes: %s' % (sel, file_size)
            job = ImageDownloadJob(url, file_name, sel)
            job.afterEvent = 'close'
            job_manager.AddJob(job)
            job_manager.failed_jobs = []
            self.session.openWithCallback(self.ImageDownloadCB, JobView, job, backgroundable=False, afterEventChangeable=False)
            return
            return

    def ImageDownloadCB(self, ret):
        if ret:
            return
        elif job_manager.active_job:
            job_manager.active_job = None
            self.close()
            return
        else:
            if len(job_manager.failed_jobs) == 0:
                self.session.openWithCallback(self.startInstall, MessageBox, _('Do you want to install this image now?'), default=False)
            else:
                self.session.open(MessageBox, _('Download Failed !!'), type=MessageBox.TYPE_ERROR)
            return
            return

    def startInstall(self, ret = None):
        if ret:
            from Plugins.Extensions.NeoBoot.plugin import InstalacjaImage
            self.session.openWithCallback(self.quit, InstalacjaImage)
        else:
            self.close()

    def layoutFinished(self):
        box = self.box()[0]
        urlbox = self.box()[1]
        stb = self.box()[2]
        print '[NeoBoot] FEED URL: ', self.feedurl
        print '[NeoBoot] BOXTYPE: ', box
        print '[NeoXBoot] URL-BOX: ', urlbox
        self.imagelist = []
        if stb != '1':
            url = self.feedurl
        elif self.distro in 'openatv':
            url = '%s/index.php?open=%s' % (self.feedurl, box)
        elif self.distro == 'openvix':
            typboxa = getTypBoxa()
            url = '%s/openvix-builds/%s' % (self.feedurl, typboxa)
        elif self.distro == 'openpli':
            url = '%s/%s' % (self.feedurl, urlbox)
        else:
            url = self.feedurl
        print '[NeoBoot] URL: ', url
        req = urllib2.Request(url)
        try:
            response = urllib2.urlopen(req)
        except urllib2.URLError as e:
            print 'URL ERROR: %s' % e
            return

        try:
            the_page = response.read()
        except urllib2.HTTPError as e:
            print 'HTTP download ERROR: %s' % e.code
            return

        lines = the_page.split('\n')
        tt = len(box)
        if stb == '1':
            for line in lines:
                if line.find("<a href='%s/" % box) > -1:
                    t = line.find("<a href='%s/" % box)
                    if self.feed in 'openatv':
                        self.imagelist.append(line[t + tt + 10:t + tt + tt + 39])
                elif line.find('<a href="http://downloads.pli-images.org/builds/' + box + '/') > -1:
                    line = line[-43 - tt:-9]
                    self.imagelist.append(line)
                elif line.find('href="openvix-') > -1:
                    t4 = line.find('openvix-')
                    t5 = line.find('.zip"')
                    self.imagelist.append(line[t4:t5 + 4])

        else:
            self.imagelist.append(stb)
        self['imageList'].l.setList(self.imagelist)


class ImageDownloadJob(Job):

    def __init__(self, url, filename, file):
        Job.__init__(self, _('Downloading %s' % file))
        ImageDownloadTask(self, url, filename)


class DownloaderPostcondition(Condition):

    def check(self, task):
        return task.returncode == 0

    def getErrorMessage(self, task):
        return self.error_message


class ImageDownloadTask(Task):

    def __init__(self, job, url, path):
        Task.__init__(self, job, _('Downloading'))
        self.postconditions.append(DownloaderPostcondition())
        self.job = job
        self.url = url
        self.path = path
        self.error_message = ''
        self.last_recvbytes = 0
        self.error_message = None
        self.download = None
        self.aborted = False
        return

    def run(self, callback):
        self.callback = callback
        self.download = downloadWithProgress(self.url, self.path)
        self.download.addProgress(self.download_progress)
        self.download.start().addCallback(self.download_finished).addErrback(self.download_failed)
        print '[ImageDownloadTask] downloading', self.url, 'to', self.path

    def abort(self):
        print '[ImageDownloadTask] aborting', self.url
        if self.download:
            self.download.stop()
        self.aborted = True

    def download_progress(self, recvbytes, totalbytes):
        if recvbytes - self.last_recvbytes > 10000:
            self.progress = int(100 * (float(recvbytes) / float(totalbytes)))
            self.name = _('Downloading') + ' ' + '%d of %d kBytes' % (recvbytes / 1024, totalbytes / 1024)
            self.last_recvbytes = recvbytes

    def download_failed(self, failure_instance = None, error_message = ''):
        self.error_message = error_message
        if error_message == '' and failure_instance is not None:
            self.error_message = failure_instance.getErrorMessage()
        Task.processFinished(self, 1)
        return

    def download_finished(self, string = ''):
        if self.aborted:
            self.finish(aborted=True)
        else:
            Task.processFinished(self, 0)