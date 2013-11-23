#!/usr/bin/env python
"""
Keep you Mac application settings in sync

Copyright (C) 2013 Laurent Raufaste <http://glop.org/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

###########
# Imports #
###########


import argparse
import base64
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tempfile

# Py3k compatible
try:
    import configparser
except ImportError:
    import ConfigParser as configparser


#######################
# Commonly used paths #
#######################

DBAS_DB_PATH = 'Dbas'
PREFERENCES = 'Library/Preferences/'
APP_SUPPORT = 'Library/Application Support/'

#################
# Configuration #
#################

# Applications supported
# Format:
# Application Name: List of files (relative path from the user's home)

SUPPORTED_APPS = {
    'ABBY FineReader for ScanSnap': [PREFERENCES + 'com.abbyy.FineReaderForScanSnap.plist'],

    'Ack': ['.ackrc'],

    'Adium': [APP_SUPPORT + 'Adium 2.0',
              PREFERENCES + 'com.adiumX.adiumX.plist'],

    'Adobe Lightroom': [
        APP_SUPPORT + 'Adobe/Lightroom/Develop Presets',
        APP_SUPPORT + 'Adobe/Lightroom/Export Actions',
        APP_SUPPORT + 'Adobe/Lightroom/Export Presets',
        APP_SUPPORT + 'Adobe/Lightroom/Filename Templates',
        APP_SUPPORT + 'Adobe/Lightroom/Filter Presets',
        APP_SUPPORT + 'Adobe/Lightroom/Import Presets',
        APP_SUPPORT + 'Adobe/Lightroom/Keyword Sets',
        APP_SUPPORT + 'Adobe/Lightroom/Label Sets',
        APP_SUPPORT + 'Adobe/Lightroom/Local Adjustment Presets',
        APP_SUPPORT + 'Adobe/Lightroom/Locations',
        APP_SUPPORT + 'Adobe/Lightroom/Metadata Presets',
        APP_SUPPORT + 'Adobe/Lightroom/Modules',
        APP_SUPPORT + 'Adobe/Lightroom/Plugins',
        APP_SUPPORT + 'Adobe/Lightroom/Watermarks'],

    'Alfred 2': [APP_SUPPORT + 'Alfred 2',
        PREFERENCES + 'com.runningwithcrayons.Alfred-2.plist'],

    'AppCode 2': [APP_SUPPORT + 'appCode20',
                  PREFERENCES + 'appCode20'],

    'Bartender': [PREFERENCES + 'com.surteesstudios.Bartender.plist'],

    'Bash': ['.bash_aliases',
             '.bash_logout',
             '.bashrc',
             '.profile',
             '.bash_profile',
             '.inputrc'],

    'Bash it': ['.bash_it'],

    'BetterSnapTool': [
        PREFERENCES + 'com.hegenberg.BetterSnapTool.plist',
        APP_SUPPORT + 'BetterSnapTool'],

    'BetterTouchTool': [
        PREFERENCES + 'com.hegenberg.BetterTouchTool.plist',
        APP_SUPPORT + 'BetterTouchTool'],

    'BibDesk': [PREFERENCES + 'edu.ucsd.cs.mmccrack.bibdesk.plist'],

    'Boto': ['.boto'],

    'Bundler': ['.bundler'],

    'Byobu': ['.byobu',
              '.byoburc',
              '.byoburc.tmux',
              '.byoburc.screen'],

    'Caffeine': [PREFERENCES + 'com.lightheadsw.Caffeine.plist'],

    'Cardiris for ScanSnap': [PREFERENCES + 'Cardiris Prefs'],

    'Chef': ['.chef'],

    'ClipMenu': [APP_SUPPORT + 'ClipMenu',
                 PREFERENCES + 'com.naotaka.ClipMenu.plist'],

    'CloudApp': [PREFERENCES + 'com.linebreak.CloudAppMacOSX.plist'],

    'Colloquy': [PREFERENCES + 'info.colloquy.plist',
                 APP_SUPPORT + 'Colloquy'],

    'Concentrate': [APP_SUPPORT + 'Concentrate/Concentrate.sqlite3'],

    'ControlPlane': [PREFERENCES + 'com.dustinrue.ControlPlane.plist'],

    'CoRD': [APP_SUPPORT + 'CoRD'],

    'Coda 2': [APP_SUPPORT + 'Coda 2',
               PREFERENCES + 'com.panic.Coda2.plist'],

    'Curl': ['.netrc'],

    'Cyberduck': [APP_SUPPORT + 'Cyberduck',
        PREFERENCES + 'ch.sudo.cyberduck.plist'],

    'Dash': [APP_SUPPORT + 'Dash/DocSets',
        APP_SUPPORT + 'Dash/library.dash',
        PREFERENCES + 'com.kapeli.dash.plist'],
    
    'Divvy': [PREFERENCES + 'com.mizage.direct.Divvy.plist'],

    'Droplr': [PREFERENCES + 'com.droplr.droplr-mac.plist'],

    'Emacs': ['.emacs',
              '.emacs.d'],

    'Ember': ['Library/Group Containers/P97H7FTHWN.com.realmacsoftware.ember'],

    'Exercism': ['.exercism'],

    'ExpanDrive': [APP_SUPPORT + 'ExpanDrive'],

    'Fantastical': [PREFERENCES + 'com.flexibits.fantastical.plist'],

    'Filezilla': ['.filezilla/'],

    'Fish': ['.config/fish'],

    'Flux': [PREFERENCES + 'org.herf.Flux.plist'],

    'ForkLift 2': [PREFERENCES + 'com.binarynights.ForkLift2.plist'],

    'GeekTool': [
        PREFERENCES + 'org.tynsoe.GeekTool.plist',
        PREFERENCES + 'org.tynsoe.geeklet.file.plist',
        PREFERENCES + 'org.tynsoe.geeklet.image.plist',
        PREFERENCES + 'org.tynsoe.geeklet.shell.plist',
        PREFERENCES + 'org.tynsoe.geektool3.plist'],

    'Git': ['.gitconfig',
            '.gitignore_global'],

    'Gitbox': [PREFERENCES + 'com.oleganza.gitbox.plist'],

    'Git Hooks': ['.git_hooks'],

    'GnuPG': ['.gnupg'],

    'Heroku': ['.heroku/accounts', '.heroku/plugins'],

    'Htop': ['.htoprc'],

    'IntelliJIdea 12': [APP_SUPPORT + 'IntelliJIdea12',
                        PREFERENCES + 'IntelliJIdea12'],

    'iTerm2': [PREFERENCES + 'com.googlecode.iterm2.plist'],

    'Irssi': ['.irssi'],

    'iWork Templates': [APP_SUPPORT + "iWork"],

    'Janus': ['.janus'],

    'Kaleidoscope': [APP_SUPPORT + 'Kaleidoscope',
        PREFERENCES + 'com.blackpixel.kaleidoscope.plist'],

    'Keymo': [PREFERENCES + 'com.manytricks.Keymo.plist'],

    'KeyRemap4MacBook': [
        PREFERENCES + 'org.pqrs.KeyRemap4MacBook.plist',
        PREFERENCES + 'org.pqrs.KeyRemap4MacBook.multitouchextension.plist',
        APP_SUPPORT + 'KeyRemap4MacBook/private.xml'],

    'LaTeXiT': [PREFERENCES + 'fr.chachatelier.pierre.LaTeXiT.plist'],

    'LimeChat': [APP_SUPPORT + 'LimeChat',
        PREFERENCES + 'net.limechat.LimeChat.plist'],


    'Dbas': ['.dbas.cfg'],

    'Mailplane': [PREFERENCES + 'com.mailplaneapp.Mailplane.plist'],

    'MacOSX': ['.MacOSX',
               'Library/ColorSync/Profiles'],

    'MacVim': [PREFERENCES + 'org.vim.MacVim.LSSharedFileList.plist',
               PREFERENCES + 'org.vim.MacVim.plist'],

    'MenuMeters': [PREFERENCES + 'com.ragingmenace.MenuMeters.plist'],

    'Mercurial': ['.hgrc',
                  '.hgignore_global'],

    'Moom': [
        PREFERENCES + 'com.manytricks.Moom.plist',
        APP_SUPPORT + 'Many Tricks'],

    'MPV': ['.mpv/channels.conf',
            '.mpv/config',
            '.mpv/input.conf'],

    'MercuryMover': [PREFERENCES + 'com.heliumfoot.MyWiAgent.plist'],

    'Nano': ['.nanorc'],

    'nvALT': [PREFERENCES + 'net.elasticthreads.nv.plist',
              APP_SUPPORT + 'Notational Velocity',
              APP_SUPPORT + 'Notational Data'],

    'Oh My Zsh': ['.oh-my-zsh'],

    'OmniFocus': [
        APP_SUPPORT + 'OmniFocus/Plug-Ins',
        APP_SUPPORT + 'OmniFocus/Themes'],

    'Pastebot': [
        PREFERENCES + 'com.tapbots.PastebotSync.plist',
        PREFERENCES + 'com.tapbots.PastebotSync.prefPane.plist',
        PREFERENCES + 'com.tapbots.PastebotSync.stats.plist'],

    'PCKeyboardHack': [PREFERENCES + 'org.pqrs.PCKeyboardHack.plist'],

    'Pear': ['.pearrc'],

    'PhpStorm 6': [APP_SUPPORT + 'WebIde60',
                   PREFERENCES + 'WebIde60',
                   PREFERENCES + 'com.jetbrains.PhpStorm.plist'],

    'PhpStorm 7': [APP_SUPPORT + 'WebIde70',
                   PREFERENCES + 'WebIde70'],

    'pip': ['.pip/pip.cfg'],

    'PopClip': [
        PREFERENCES + 'com.pilotmoon.popclip.plist',
        APP_SUPPORT + 'PopClip'],

    'Pow': ['.powconfig',
            '.powenv',
            '.powrc'],

    'PyPI': ['.pypirc'],

    'Quicklook': ['Library/Quicklook'],

    'Quicksilver': [PREFERENCES + 'com.blacktree.Quicksilver.plist',
                    APP_SUPPORT + 'Quicksilver'],

    'Rails': ['.railsrc'],

    'Ruby': ['.gemrc',
             '.irbrc',
             '.gem',
             '.pryrc',
             '.aprc'],

    'RubyMine 4': [APP_SUPPORT + 'RubyMine40',
                   PREFERENCES + 'RubyMine40'],

    'RubyMine 5': [APP_SUPPORT + 'RubyMine50',
                   PREFERENCES + 'RubyMine50'],

    'Ruby Version': ['.ruby-version'],

    'Pentadactyl': ['.pentadactyl',
                    '.pentadactylrc'],

    'S3cmd': ['.s3cfg'],

    'ScanSnap Manager V3.2': [PREFERENCES + 'jp.co.pfu.ScanSnap.P2IUNISET.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.QMScanToPrint.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.Scan2EN2Setting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.Scan2Folder.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.Scan2FolderSetting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.Scan2GDocSetting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.Scan2MailSetting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.Scan2MobileSetting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.Scan2PrintSetting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.ScanToDropboxSetting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.ScanToFolder.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.ScanToSalesforceSetting.plist',
                              PREFERENCES + 'jp.co.pfu.ScanSnap.V10L10.plist'],

    'Scenario': [PREFERENCES + 'com.lagente.scenario.plist',
                 'Library/Scenario'],

    'Scripts': ['Library/Scripts'],

    'Screen': ['.screenrc'],

    'SelfControl': [PREFERENCES + 'org.eyebeam.SelfControl.plist'],

    'Sequel Pro': [APP_SUPPORT + 'Sequel Pro/Data'],

    'Services': ['Library/Services'],

    'SHSH Blobs': ['.shsh'],

    'Shuttle': ['.shuttle.json'],

    'SizeUp': [PREFERENCES + 'com.irradiatedsoftware.SizeUp.plist',
               APP_SUPPORT + 'SizeUp/SizeUp.sizeuplicense'],

    'Skim': [PREFERENCES + 'net.sourceforge.skim-app.skim.plist'],

    'Skype': [PREFERENCES + 'com.skype.skype.plist',
              APP_SUPPORT + 'Skype'],

    'Slate': ['.slate',
              APP_SUPPORT + 'com.slate.Slate'],

    'Slogger': ['Slogger'],

    'SourceTree': [APP_SUPPORT + 'SourceTree/sourcetree.license',
                   APP_SUPPORT + 'SourceTree/browser.plist',
                   APP_SUPPORT + 'SourceTree/hgrc_sourcetree',
                   APP_SUPPORT + 'SourceTree/hostingservices.plist',
                   PREFERENCES + 'com.torusknot.SourceTree.plist',
                   PREFERENCES + 'com.torusknot.SourceTreeNotMAS.plist'],

    'Spark': [APP_SUPPORT + 'Spark'],

    'Spectacle': [PREFERENCES + 'com.divisiblebyzero.Spectacle.plist'],

    'Spotify' : [PREFERENCES + 'com.spotify.client.plist'],

    'SSH': ['.ssh'],

    'Stata': [APP_SUPPORT + 'Stata',
              PREFERENCES + 'com.stata.stata12.plist',
              PREFERENCES + 'com.stata.stata13.plist'],

    'Sublime Text 2': [APP_SUPPORT + 'Sublime Text 2/Installed Packages',
                       APP_SUPPORT + 'Sublime Text 2/Packages',
                       APP_SUPPORT + 'Sublime Text 2/Pristine Packages',
                       APP_SUPPORT + 'Sublime Text 2/Settings'],

    'Sublime Text 3': [APP_SUPPORT + 'Sublime Text 3/Installed Packages',
                       APP_SUPPORT + 'Sublime Text 3/Packages'],

    'Subversion': ['.subversion'],

    'SuperDuper!': [APP_SUPPORT + 'SuperDuper!'],


    'Teamocil': ['.teamocil'],

    'TextMate': [APP_SUPPORT + 'TextMate',
                 PREFERENCES + 'com.macromates.textmate.plist',
                 PREFERENCES + 'com.macromates.textmate.webpreview.plist'],

    'TextMate GetBundles': [PREFERENCES + 'com.macromates.textmate.getbundles.plist'],

    'TextWrangler': [APP_SUPPORT + 'TextWrangler',
                     PREFERENCES + 'com.barebones.textwrangler.PreferenceData',
                     PREFERENCES + 'com.barebones.textwrangler.plist'],

    'Tmux': ['.tmux.conf'],

    'Tmuxinator': ['.tmuxinator'],

    'TotalFinder': [PREFERENCES + 'com.binaryage.totalfinder.crashwatcher.plist',
                    PREFERENCES + 'com.binaryage.totalfinder.plist'],

    'TotalTerminal': [PREFERENCES + 'com.binaryage.totalterminal.crashwatcher.plist',
                      PREFERENCES + 'com.binaryage.totalterminal.plist'],

    'Tower': [APP_SUPPORT + 'Tower',
              PREFERENCES + 'com.fournova.Tower.plist'],

    'Transmission': [PREFERENCES + 'org.m0k.transmission.plist'],

    'Transmit': [
        PREFERENCES + 'com.panic.Transmit.plist',
        APP_SUPPORT + 'Transmit/Metadata',
        APP_SUPPORT + 'Transmit/Favorites'
    ],

    'Twitterrific': [APP_SUPPORT + 'Twitterrific'],

    'VelaClock': [PREFERENCES + 'widget-com.veladg.widget.velaclockdeluxe.plist',
                  PREFERENCES + 'com.veladg.vcDeluxeReg.plist',
                  APP_SUPPORT + 'VelaClock',
                  APP_SUPPORT + 'Vela Design Group'],

    'VelaTerra': [PREFERENCES + 'com.veladg.VelaTerra.plist',
                  APP_SUPPORT + 'VelaTerra'],

    'Ventrilo': [PREFERENCES + 'Ventrilo'],

    'Vim': ['.gvimrc',
            '.gvimrc.before',
            '.gvimrc.after',
            '.vim',
            '.vimrc',
            '.vimrc.before',
            '.vimrc.after'],

    'Vimperator': ['.vimperator',
                   '.vimperatorrc'],

    'Viscosity': [APP_SUPPORT + 'Viscosity',
                  PREFERENCES + 'com.viscosityvpn.Viscosity.plist'],

    'Witch': [PREFERENCES + 'com.manytricks.Witch.plist'],

    'X11': ['.Xresources',
            '.fonts'],

    'Xcode': ['Library/Developer/Xcode/UserData/CodeSnippets',
              'Library/Developer/Xcode/UserData/FontAndColorThemes',
              'Library/Developer/Xcode/UserData/KeyBindings',
              'Library/Developer/Xcode/UserData/SearchScopes.xcsclist'],

    'XEmacs': ['.xemacs'],

    'Zsh': ['.zshenv',
            '.zprofile',
            '.zshrc',
            '.zlogin',
            '.zlogout'],
    }

#############
# Constants #
#############


# Current version
VERSION = '0.5.2'

# Mode used to backup files to Dropbox
BACKUP_MODE = 'backup'

# Mode used to restore files from Dropbox
RESTORE_MODE = 'restore'

# Mode used to remove Dbas and reset and config file
UNINSTALL_MODE = 'uninstall'

# Support platforms
PLATFORM_DARWIN = 'Darwin'
PLATFORM_LINUX = 'Linux'


###########
# Classes #
###########


class ApplicationProfile(object):
    """Instantiate this class with application specific data"""

    def __init__(self, dbas, files):
        """
        Create an ApplicationProfile instance

        Args:
            dbas (Dbas)
            files (list)
        """
        assert isinstance(dbas, Dbas)
        assert isinstance(files, list)

        self.dbas = dbas
        self.files = files

    def backup(self):
        """
        Backup the application config files

        Algorithm:
            if exists home/file
              if home/file is a real file
                if exists dbas/file
                  are you sure ?
                  if sure
                    rm dbas/file
                    mv home/file dbas/file
                    link dbas/file home/file
                else
                  mv home/file dbas/file
                  link dbas/file home/file
        """

        # For each file used by the application
        for filename in self.files:
            # Get the full path of each file
            filepath = os.path.join(os.environ['HOME'], filename)
            dbas_filepath = os.path.join(self.dbas.dbas_folder, filename)

            # If the file exists and is not already a link pointing to Dbas
            if ((os.path.isfile(filepath) or os.path.isdir(filepath))
                and not (os.path.islink(filepath)
                         and (os.path.isfile(dbas_filepath)
                              or os.path.isdir(dbas_filepath))
                         and os.path.samefile(filepath, dbas_filepath))):

                print "Backing up {}...".format(filename)

                # Check if we already have a backup
                if os.path.exists(dbas_filepath):

                    # Name it right
                    if os.path.isfile(dbas_filepath):
                        file_type = 'file'
                    elif os.path.isdir(dbas_filepath):
                        file_type = 'folder'
                    elif os.path.islink(dbas_filepath):
                        file_type = 'link'
                    else:
                        raise ValueError("Unsupported file: {}"
                                         .format(dbas_filepath))

                    # Ask the user if he really want to replace it
                    if confirm("A {} named {} already exists in the backup."
                               "\nAre you sure that your want to replace it ?"
                               .format(file_type, dbas_filepath)):
                        # Delete the file in Dbas
                        delete(dbas_filepath)
                        # Copy the file
                        copy(filepath, dbas_filepath)
                        # Delete the file in the home
                        delete(filepath)
                        # Link the backuped file to its original place
                        link(dbas_filepath, filepath)
                else:
                    # Copy the file
                    copy(filepath, dbas_filepath)
                    # Delete the file in the home
                    delete(filepath)
                    # Link the backuped file to its original place
                    link(dbas_filepath, filepath)

    def restore(self):
        """
        Restore the application config files

        Algorithm:
            if exists dbas/file
              if exists home/file
                are you sure ?
                if sure
                  rm home/file
                  link dbas/file home/file
              else
                link dbas/file home/file
        """

        # For each file used by the application
        for filename in self.files:
            # Get the full path of each file
            dbas_filepath = os.path.join(self.dbas.dbas_folder, filename)
            home_filepath = os.path.join(os.environ['HOME'], filename)

            # If the file exists and is not already pointing to the dbas file
            # and the folder makes sense on the current platform (Don't sync
            # any subfolder of ~/Library on GNU/Linux)
            if ((os.path.isfile(dbas_filepath)
                 or os.path.isdir(dbas_filepath))
                and not (os.path.islink(home_filepath)
                         and os.path.samefile(dbas_filepath,
                                              home_filepath))
                and can_file_be_synced_on_current_platform(filename)):

                print "Restoring {}...".format(filename)

                # Check if there is already a file in the home folder
                if os.path.exists(home_filepath):
                    # Name it right
                    if os.path.isfile(home_filepath):
                        file_type = 'file'
                    elif os.path.isdir(home_filepath):
                        file_type = 'folder'
                    elif os.path.islink(home_filepath):
                        file_type = 'link'
                    else:
                        raise ValueError("Unsupported file: {}"
                                         .format(dbas_filepath))

                    if confirm("You already have a {} named {} in your home."
                               "\nDo you want to replace it with your backup ?"
                               .format(file_type, filename)):
                        delete(home_filepath)
                        link(dbas_filepath, home_filepath)
                else:
                    link(dbas_filepath, home_filepath)

    def uninstall(self):
        """
        Uninstall Dbas.
        Restore any file where it was before the 1st Dbas backup.

        Algorithm:
            for each file in config
                if dbas/file exists
                    if home/file exists
                        delete home/file
                    copy dbas/file home/file
            delete the dbas folder
            print how to delete dbas
        """
        # For each file used by the application
        for filename in self.files:
            # Get the full path of each file
            dbas_filepath = os.path.join(self.dbas.dbas_folder, filename)
            home_filepath = os.path.join(os.environ['HOME'], filename)

            # If the dbas file exists
            if (os.path.isfile(dbas_filepath)
                or os.path.isdir(dbas_filepath)):

                # Check if there is a corresponding file in the home folder
                if os.path.exists(home_filepath):
                    # If there is, delete it as we are gonna copy the Dropbox
                    # one there
                    delete(home_filepath)

                    # Copy the Dropbox file to the home folder
                    copy(dbas_filepath, home_filepath)


class Dbas(object):
    """Main Dbas class"""

    def __init__(self):
        """Dbas Constructor"""
        try:
            self.dropbox_folder = get_dropbox_folder_location()
        except IOError:
            error(("Unable to find the Dropbox folder."
                   " If Dropbox is not installed and running, go for it on"
                   " <http://www.dropbox.com/>"))

        self.dbas_folder = os.path.join(self.dropbox_folder, DBAS_DB_PATH)
        self.temp_folder = tempfile.mkdtemp(prefix="dbas_tmp_")

    def _check_for_usable_environment(self):
        """Check if the current env is usable and has everything's required"""

        # Do we have a home folder ?
        if not os.path.isdir(self.dropbox_folder):
            error(("Unable to find the Dropbox folder."
                   " If Dropbox is not installed and running, go for it on"
                   " <http://www.dropbox.com/>"))

        # Is Sublime Text running ?
        #if is_process_running('Sublime Text'):
        #    error(("Sublime Text is running. It is known to cause problems"
        #           " when Sublime Text is running while I backup or restore"
        #           " its configuration files. Please close Sublime Text and"
        #           " run me again."))

    def check_for_usable_backup_env(self):
        """Check if the current env can be used to back up files"""
        self._check_for_usable_environment()
        self.create_dbas_home()

    def check_for_usable_restore_env(self):
        """Check if the current env can be used to restore files"""
        self._check_for_usable_environment()

        if not os.path.isdir(self.dbas_folder):
            error("Unable to find the Dbas folder: {}\n"
                  "You might want to backup some files or get your Dropbox"
                  " folder synced first."
                  .format(self.dbas_folder))

    def clean_temp_folder(self):
        """Delete the temp folder and files created while running"""
        shutil.rmtree(self.temp_folder)

    def create_dbas_home(self):
        """If the Dbas home folder does not exist, create it"""
        if not os.path.isdir(self.dbas_folder):
            if confirm("Dbas needs a folder to store your configuration "
                       " files\nDo you want to create it now ? <{}>"
                       .format(self.dbas_folder)):
                os.mkdir(self.dbas_folder)
            else:
                error("Dbas can't do anything without a home =(")


####################
# Useful functions #
####################


def confirm(question):
    """
    Ask the user if he really want something to happen

    Args:
        question(str): What can happen

    Returns:
        (boolean): Confirmed or not
    """
    while True:
        answer = raw_input(question + ' <Yes|No>')
        if answer == 'Yes':
            confirmed = True
            break
        if answer == 'No':
            confirmed = False
            break

    return confirmed


def delete(filepath):
    """
    Delete the given file, directory or link.
    Should support undelete later on.

    Args:
        filepath (str): Absolute full path to a file. e.g. /path/to/file
    """
    # Some files have ACLs, let's remove them recursively
    remove_acl(filepath)

    # Some files have immutable attributes, let's remove them recursively
    remove_immutable_attribute(filepath)

    # Finally remove the files and folders
    if os.path.isfile(filepath) or os.path.islink(filepath):
        os.remove(filepath)
    elif os.path.isdir(filepath):
        shutil.rmtree(filepath)


def copy(src, dst):
    """
    Copy a file or a folder (recursively) from src to dst.
    For simplicity sake, both src and dst must be absolute path and must
    include the filename of the file or folder.
    Also do not include any trailing slash.

    e.g. copy('/path/to/src_file', '/path/to/dst_file')
    or copy('/path/to/src_folder', '/path/to/dst_folder')

    But not: copy('/path/to/src_file', 'path/to/')
    or copy('/path/to/src_folder/', '/path/to/dst_folder')

    Args:
        src (str): Source file or folder
        dst (str): Destination file or folder
    """
    assert isinstance(src, str) or isinstance(src, unicode)
    assert os.path.exists(src)
    assert isinstance(dst, str) or isinstance(src, unicode)

    # Create the path to the dst file if it does not exists
    abs_path = os.path.dirname(os.path.abspath(dst))
    if not os.path.isdir(abs_path):
        os.makedirs(abs_path)

    # We need to copy a single file
    if os.path.isfile(src):
        # Copy the src file to dst
        shutil.copy(src, dst)

    # We need to copy a whole folder
    elif os.path.isdir(src):
        shutil.copytree(src, dst)

    # What the heck is this ?
    else:
        raise ValueError("Unsupported file: {}".format(src))

    # Set the good mode to the file or folder recursively
    chmod(dst)


def link(target, link):
    """
    Create a link to a target file or a folder.
    For simplicity sake, both target and link must be absolute path and must
    include the filename of the file or folder.
    Also do not include any trailing slash.

    e.g. link('/path/to/file', '/path/to/link')

    But not: link('/path/to/file', 'path/to/')
    or link('/path/to/folder/', '/path/to/link')

    Args:
        target (str): file or folder the link will point to
        link (str): Link to create
    """
    assert isinstance(target, str) or isinstance(target, unicode)
    assert os.path.exists(target)
    assert isinstance(link, str) or isinstance(target, unicode)

    # Create the path to the link if it does not exists
    abs_path = os.path.dirname(os.path.abspath(link))
    if not os.path.isdir(abs_path):
        os.makedirs(abs_path)

    # Make sure the file or folder recursively has the good mode
    chmod(target)

    # Create the link to target
    os.symlink(target, link)


def chmod(target):
    """
    Recursively set the chmod for files to 0600 and 0700 for folders.
    It's ok unless we need something more specific.

    Args:
        target (str): Root file or folder
    """
    assert isinstance(target, str) or isinstance(target, unicode)
    assert os.path.exists(target)

    file_mode = stat.S_IRUSR | stat.S_IWUSR
    folder_mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR

    # Remove the immutable attribute recursively if there is one
    remove_immutable_attribute(target)

    if os.path.isfile(target):
        os.chmod(target, file_mode)

    elif os.path.isdir(target):
        # chmod the root item
        os.chmod(target, folder_mode)

        # chmod recursively in the folder it it's one
        for root, dirs, files in os.walk(target):
            for cur_dir in dirs:
                os.chmod(os.path.join(root, cur_dir), folder_mode)
            for cur_file in files:
                os.chmod(os.path.join(root, cur_file), file_mode)

    else:
        raise ValueError("Unsupported file type: {}".format(target))


def error(message):
    """
    Throw an error with the given message and immediately quit.

    Args:
        message(str): The message to display.
    """
    sys.exit("Error: {}".format(message))


def parse_cmdline_args():
    """
    Setup the engine that's gonna parse the command line arguments

    Returns:
        (argparse.Namespace)
    """

    # Format some epilog text
    epilog = "Supported applications: "
    epilog += ', '.join(sorted(SUPPORTED_APPS.iterkeys()))
    epilog += "\n\nDbas requires a fully synced Dropbox folder."

    # Setup the global parser
    parser = argparse.ArgumentParser(
        description=("Dbas {}\n"
                     "Keep you application settings in sync.\n"
                     "Copyright (C) 2013 Laurent Raufaste <http://glop.org/>\n"
                     .format(VERSION)),
        epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    # Add the required arg
    parser.add_argument("mode",
                        choices=[BACKUP_MODE, RESTORE_MODE, UNINSTALL_MODE],
                        help=("Backup will sync your conf files to Dropbox,"
                              " use this the 1st time you use Dbas.\n"
                              "Restore will link the conf files already in"
                              " Dropbox on your system, use it on any new"
                              " system you use.\n"
                              "Uninstall will reset everything as it was"
                              " before using Dbas."))

    # Parse the command line and return the parsed options
    return parser.parse_args()


def get_dropbox_folder_location():
    """
    Try to locate the Dropbox folder

    Returns:
        (str) Full path to the current Dropbox folder
    """
    host_db_path = os.environ['HOME'] + '/.dropbox/host.db'
    with open(host_db_path, 'r') as f:
        data = f.read().split()
    dropbox_home = base64.b64decode(data[1])

    return dropbox_home


def get_ignored_apps():
    """
    Get the list of applications ignored in the config file

    Returns:
        (set) List of application names to ignore, lowercase
    """
    # If a config file exists, grab it and parser it
    config = configparser.SafeConfigParser(allow_no_value=True)

    # We ignore nothing by default
    ignored_apps = []

    # Is the config file there ?
    if config.read(os.environ['HOME'] + '/.dbas.cfg'):
        # Is the "Ignored Applications" in the cfg file ?
        if config.has_section('Ignored Applications'):
            ignored_apps = config.options('Ignored Applications')

    return set(ignored_apps)

def get_config_path_and_append_to_backup(section, optionName, dbas):
    """
    Looks in the config for the specified option in the specified section.  If it is there,
    it reads the value and parses it as a path.  If the path is valid, it appends the path
    to the list of files to backup for the 'Dbas' application entry.

    Args:
        section(str): The section in the config file
        optionName(str): The option name to look for
        dbas(Dbas): the instance that is running

    Returns:
        The path if it is valid and exists, the empty string otherwise.
    """
    # If a config file exists, grab it and parser it
    config = configparser.SafeConfigParser(allow_no_value=True)

    # Is the config file there (be sure to check the backup dir since it may not have been copied yet) ?
    if config.read(os.environ['HOME'] + '/.dbas.cfg') or config.read(dbas.dbas_folder + '/.dbas.cfg'):
        # Is the section/option pair in the cfg file ?
        if config.has_option(section,optionName):
            path = os.path.expanduser( config.get(section,optionName))
            relPath = os.path.relpath(path, os.environ['HOME'])
            # Is the specified path valid (either on the real system or in the backup) ?
            if os.path.exists(path): 
                SUPPORTED_APPS['Dbas'].append(relPath)
                return path;
            elif os.path.exists(dbas.dbas_folder + '/' + relPath):
                SUPPORTED_APPS['Dbas'].append(relPath)
                return dbas.dbas_folder + '/' + relPath

    return "";



def get_custom_apps(dbas):
    """
    Get the list of custom applications referenced in the config file and
    reads it in as a dictionary.

    Args:
        dbas(Dbas) the instance that is running

    Returns:
        (dictionary) Applications / files to backup or an empy dictionary
        if the user didn't specify any custom applications
    """
    path = get_config_path_and_append_to_backup('Custom Applications', 'dictionaryFile', dbas)
    if path:
        json_data=open(path).read()
        return json.loads(json_data)

    return {}

def get_allowed_apps():
    """
    Get the list of applications allowed in the config file

    Returns:
        (set) list of applciation names to backup
    """

    # If a config file exists, grab it and parser it
    config = configparser.SafeConfigParser(allow_no_value=True)

    # We allow all by default
    allowed_apps = set(SUPPORTED_APPS)

    # Is the config file there ?
    if config.read(os.environ['HOME'] + '/.dbas.cfg'):
        # Is the "Allowed Applications" in the cfg file ?
        if config.has_section('Allowed Applications'):
            # Reset allowed apps to include only the user-defined
            allowed_apps = set()
            for app_name in SUPPORTED_APPS:
                if app_name.lower() in config.options('Allowed Applications'):
                    allowed_apps.add(app_name)

    return allowed_apps


def get_apps_to_backup():
    """
    Get the list of application that should be backup by Dbas.
    It's the list of allowed apps minus the list of ignored apps.

    Returns:
        (set) List of application names to backup
    """
    apps_to_backup = set()
    apps_to_ignore = get_ignored_apps()
    apps_to_allow = get_allowed_apps()

    for app_name in apps_to_allow:
        if app_name.lower() not in apps_to_ignore:
            apps_to_backup.add(app_name)

    return apps_to_backup


def is_process_running(process_name):
    """
    Check if a process with the given name is running

    Args:
        (str): Process name, e.g. "Sublime Text"

    Returns:
        (bool): True if the process is running
    """
    is_running = False

    # On systems with pgrep, check if the given process is running
    if os.path.isfile('/usr/bin/pgrep'):
        DEVNULL = open(os.devnull, 'wb')
        returncode = subprocess.call(['/usr/bin/pgrep', process_name],
                                     stdout=DEVNULL)
        is_running = bool(returncode == 0)

    return is_running


def remove_acl(path):
    """
    Remove the ACL of the file or folder located on the given path.
    Also remove the ACL of any file and folder below the given one,
    recursively.

    Args:
        path (str): Path to the file or folder to remove the ACL for,
                    recursively.
    """
    # Some files have ACLs, let's remove them recursively
    if platform.system() == PLATFORM_DARWIN and os.path.isfile('/bin/chmod'):
        subprocess.call(['/bin/chmod', '-R', '-N', path])
    elif ((platform.system() == PLATFORM_LINUX)
          and os.path.isfile('/bin/setfacl')):
        subprocess.call(['/bin/setfacl', '-R', '-b', path])


def remove_immutable_attribute(path):
    """
    Remove the immutable attribute of the file or folder located on the given
    path. Also remove the immutable attribute of any file and folder below the
    given one, recursively.

    Args:
        path (str): Path to the file or folder to remove the immutable
                    attribute for, recursively.
    """
    # Some files have ACLs, let's remove them recursively
    if ((platform.system() == PLATFORM_DARWIN)
        and os.path.isfile('/usr/bin/chflags')):
        subprocess.call(['/usr/bin/chflags', '-R', 'nouchg', path])
    elif (platform.system() == PLATFORM_LINUX
          and os.path.isfile('/usr/bin/chattr')):
        subprocess.call(['/usr/bin/chattr', '-R', '-i', path])


def can_file_be_synced_on_current_platform(path):
    """
    Check if it makes sens to sync the file at the given path on the current
    platform.
    For now we don't sync any file in the ~/Library folder on GNU/Linux.
    There might be other exceptions in the future.

    Args:
        (str): Path to the file or folder to check. If relative, prepend it
               with the home folder.
               'abc' becomes '~/abc'
               '/def' stays '/def'

    Returns:
        (bool): True if given file can be synced
    """
    can_be_synced = True

    # If the given path is relative, prepend home
    fullpath = os.path.join(os.environ['HOME'], path)

    # Compute the ~/Library path on OS X
    # End it with a slash because we are looking for this specific folder and
    # not any file/folder named LibrarySomething
    library_path = os.path.join(os.environ['HOME'], 'Library/')

    if platform.system() == PLATFORM_LINUX:
        if fullpath.startswith(library_path):
            can_be_synced = False

    return can_be_synced

def update_supported_apps(dbas):
    """
    Get the list of custom apps that the user has specified 
    (if any) and append it to the SUPPORTED_APPS list, replacing 
    any that are duplicated.

    Args:
        dbas(Dbas) the instance that is running.
    """
    SUPPORTED_APPS.update(get_custom_apps(dbas))


################
# Main Program #
################


def main():
    """Main function"""

    dbas = Dbas()

    update_supported_apps(dbas)

    # Get the command line arg
    args = parse_cmdline_args()

    if args.mode == BACKUP_MODE:
        # Check the env where the command is being run
        dbas.check_for_usable_backup_env()

        # Backup each application
        for app_name in get_apps_to_backup():
            app = ApplicationProfile(dbas, SUPPORTED_APPS[app_name])
            app.backup()

    elif args.mode == RESTORE_MODE:
        # Check the env where the command is being run
        dbas.check_for_usable_restore_env()

        # Restore 'Dbas' first to get the configs in place
        app = ApplicationProfile(dbas, SUPPORTED_APPS['Dbas'])
        app.restore()

        for app_name in SUPPORTED_APPS:
            app = ApplicationProfile(dbas, SUPPORTED_APPS[app_name])
            app.restore()

    elif args.mode == UNINSTALL_MODE:
        # Check the env where the command is being run
        dbas.check_for_usable_restore_env()

        if confirm("You are going to uninstall Dbas.\n"
                   "Every configuration file, setting and dotfile managed"
                   " by Dbas will be unlinked and moved back to their"
                   " original place, in your home folder.\n"
                   "Are you sure ?"):
            for app_name in SUPPORTED_APPS:
                app = ApplicationProfile(dbas, SUPPORTED_APPS[app_name])
                app.uninstall()

            # Delete the Dbas folder in Dropbox
            # Don't delete this as there might be other Macs that aren't
            # uninstalled yet
            # delete(dbas.dbas_folder)

            print ("\n"
                   "All your files have been put back into place. You can now"
                   " safely uninstall Dbas.\n"
                   "If you installed it by hand, you should only have to"
                   " launch this command:\n"
                   "\n"
                   "\tsudo rm {}\n"
                   "\n"
                   "Thanks for using Dbas !"
                   .format(os.path.abspath(__file__)))
    else:
        raise ValueError("Unsupported mode: {}".format(args.mode))

    # Delete the tmp folder
    dbas.clean_temp_folder()

if __name__ == "__main__":
    main()
