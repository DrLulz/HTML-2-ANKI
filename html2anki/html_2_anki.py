#!/usr/bin/env python

import os
import sys
import urllib
import urllib2
import re
#import logging as log
from BeautifulSoup import BeautifulSoup as bs
from HTMLParser import HTMLParser

# ANKI
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo

# PyQt4
from PyQt4.QtGui import *
from PyQt4.QtGui import QFileDialog
#from PyQt4.QtCore import *
from PyQt4.QtCore import Qt

#log.basicConfig(filename=os.path.expanduser('~/Desktop/log'), level=log.INFO)


def dark_theme(name, col):
    
    path = os.path.join(mw.pm.addonFolder(), 'html2anki')
    
    with open((path+'/template_front.txt'),'r') as ftemp_txt:
        ftemp = ftemp_txt.read()
    with open((path+'/template_css.txt'),'r') as css_txt:
        css = css_txt.read()
    with open((path+'/template_back.txt'),'r') as btemp_txt:
        btemp = btemp_txt.read()
    
    mm = col.models
    m  = mm.new(u'Basic'+u' ({0} DARK)'.format(name))
    
    fm = mm.newField('Front')
    mm.addField(m, fm)
    fm = mm.newField('F Note')
    mm.addField(m, fm)
    fm = mm.newField('Back')
    mm.addField(m, fm)
    fm = mm.newField('B Note')
    mm.addField(m, fm)
    fm = mm.newField('class')
    mm.addField(m, fm)
    fm = mm.newField('http')
    mm.addField(m, fm)
    
    m['css'] = css
    
    t  = mm.newTemplate('Card 1')
    t['qfmt'] = ftemp
    t['afmt'] = btemp
    mm.addTemplate(m, t)
    mm.add(m)
    return m


def basic_theme(name, col):
    
    mm = col.models
    m  = mm.new(u'Basic'+u' ({0})'.format(name))
    
    fm = mm.newField('Front')
    mm.addField(m, fm)
    fm = mm.newField('Back')
    mm.addField(m, fm)
    fm = mm.newField('http')
    mm.addField(m, fm)
    
    t  = mm.newTemplate('Card 1')
    t['qfmt'] = '{{Front}}'
    t['afmt'] = '{{FrontSide}}\n\n<hr id=answer>\n\n{{Back}}'

    mm.addTemplate(m, t)
    mm.add(m)
    return m

    

class UI(QMainWindow):

    def __init__(self):
        super(QMainWindow,self).__init__()
        self.make_UI()
        
        
    def make_UI(self):
        
        # MAIN WIDGET & LAYOUT
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # SETTINGS WIDGET
        settings_widget = QWidget()
        settings_layout = QVBoxLayout()
        settings_widget.setLayout(settings_layout)
        
        # INSTRUCTIONS WIDGET
        instructions_widget = QWidget()
        instructions_layout = QVBoxLayout()
        instructions_widget.setLayout(instructions_layout)
        
        
        ###############################################
        # R.1           USER FEEDBACK
        ###############################################    

        # LAYOUT
        feedback_box      = QGroupBox('')
        feedback_layout   = QHBoxLayout()
        feedback_box.setLayout(feedback_layout)

        # LABEL
        self.FEEDBACK = QLabel('Fill in the fields and press RUN')
        self.FEEDBACK.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.FEEDBACK.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-weight: bold;
                                      color: #CC6666;
                                      font-size: 16px;''')
        
        # ADD LABEL TO LAYOUT
        feedback_layout.addWidget(self.FEEDBACK)
        
        ### ADD FEEDBACK TO SETTINGS WIDGET
        settings_layout.addWidget(feedback_box)        
        
        
        ###############################################
        # R.2           DECK OPTIONS
        ###############################################

        # LAYOUT
        deck_box      = QGroupBox('Deck Options')
        deck_layout   = QHBoxLayout()
        deck_box.setLayout(deck_layout)
        
        # NAME
        self.DECK_LABEL = QLabel('Name:')                              
        self.DECK_FIELD = QLineEdit('', self)
        self.DECK_FIELD.setAlignment(Qt.AlignHCenter)

        # TAGS
        self.TAGS_LABEL = QLabel('Tags:')
        self.TAGS_FIELD = QLineEdit('', self)
        self.TAGS_FIELD.setAlignment(Qt.AlignHCenter)

        # ADD NAME TO LAYOUT
        deck_layout.addWidget(self.DECK_LABEL)
        deck_layout.addWidget(self.DECK_FIELD)

        # ADD TAGS TO LAYOUT
        deck_layout.addWidget(self.TAGS_LABEL)
        deck_layout.addWidget(self.TAGS_FIELD)
        
        ### ADD DECK OPTIONS TO SETTINGS WIDGET        
        settings_layout.addWidget(deck_box)
        
        
        ###############################################
        # R.3           HTML SOURCE
        ###############################################
        
        # LAYOUT
        html_box      = QGroupBox('HTML Source')
        html_layout   = QHBoxLayout()
        html_box.setLayout(html_layout)

        # FIELD
        self.HTML_LABEL  = QLabel('HTML:')                              
        self.HTML_FIELD  = QLineEdit('Paste URL or Browse', self)
        
        # BUTTON
        self.HTML_BROWSE = QPushButton('Browse', self)
        self.HTML_BROWSE.clicked.connect(self.local_file)

        # ADD FIELD TO LAYOUT
        html_layout.addWidget(self.HTML_LABEL)
        html_layout.addWidget(self.HTML_FIELD)

        # ADD BUTTON TO LAYOUT
        html_layout.addWidget(self.HTML_BROWSE)        

        ### ADD HTML SOURCE TO SETTINGS WIDGET
        settings_layout.addWidget(html_box)


        ###############################################
        # R.4       ROW 4 RIGHT/LEFT LAYOUT
        ###############################################
        
        # ROW 4 LAYOUT
        preview_row   = QHBoxLayout()
        preview_left  = QVBoxLayout()
        preview_right = QVBoxLayout()

        # ADD R/L TO R.4 LAYOUT
        preview_row.addLayout(preview_left)
        preview_row.addLayout(preview_right)

        ### ADD R.4 TO SETTINGS WIDGET
        settings_layout.addLayout(preview_row)

        
        ###############################################
        # R.4.R          ROW 4 RIGHT
        ###############################################
        
        ###############################################
        # R.4.R.1       HTML SELECTION
        ###############################################
        ''' This is what BeautifulSoup will iterate '''

        # LAYOUT
        select_box    = QGroupBox('Select')
        select_layout = QHBoxLayout()
        select_box.setLayout(select_layout)
        
        # ELEM
        self.S_FIELD_ELEM  = QLineEdit('all', self)
        self.S_FIELD_ELEM.setAlignment(Qt.AlignHCenter)
        self.S_FIELD_ELEM.setToolTip('<h5>Element:</h5><p><code>div<br />span</code></p>')
        self.S_FIELD_ELEM.textChanged.connect(self.preview_html)
        
        # ATTR
        self.S_FIELD_ATTR  = QLineEdit('class', self)
        self.S_FIELD_ATTR.setAlignment(Qt.AlignHCenter)
        self.S_FIELD_ATTR.setToolTip('<h5>Attribute:</h5><p><code>id<br />class</code></p>') 
        self.S_FIELD_ATTR.textChanged.connect(self.preview_html)       
        
        # ATTR VALUE
        self.S_FIELD_VALUE = QLineEdit('term', self)
        self.S_FIELD_VALUE.setAlignment(Qt.AlignHCenter)
        self.S_FIELD_VALUE.setToolTip('<h5>Value</h5>')
        self.S_FIELD_VALUE.textChanged.connect(self.preview_html)
        
        # ADD ELEM, ATTR & VALUE TO LAYOUT
        select_layout.addWidget(self.S_FIELD_ELEM)
        select_layout.addWidget(self.S_FIELD_ATTR)
        select_layout.addWidget(self.S_FIELD_VALUE)
        
        ## ADD SELECTION TO ROW 4 RIGHT LAYOUT
        preview_right.addWidget(select_box)
        
        
        ###############################################
        # R.4.R.2          QUESTION
        ###############################################
        
        # LAYOUT
        question_box    = QGroupBox('Question')
        question_layout = QHBoxLayout()
        question_box.setLayout(question_layout)

        # ELEM
        self.Q_FIELD_ELEM  = QLineEdit('all', self)
        self.Q_FIELD_ELEM.setAlignment(Qt.AlignHCenter)
        self.Q_FIELD_ELEM.setToolTip('<h5>Element:</h5><p><code>div<br />span</code></p>')
        self.Q_FIELD_ELEM.textChanged.connect(self.preview_html)

        # ATTR        
        self.Q_FIELD_ATTR  = QLineEdit('class', self)
        self.Q_FIELD_ATTR.setAlignment(Qt.AlignHCenter)
        self.Q_FIELD_ATTR.setToolTip('<h5>Attribute:</h5><p><code>id<br />class</code></p>') 
        self.Q_FIELD_ATTR.textChanged.connect(self.preview_html)       
        
        # ATTR VALUE        
        self.Q_FIELD_VALUE = QLineEdit('qWord', self)
        self.Q_FIELD_VALUE.setAlignment(Qt.AlignHCenter)
        self.Q_FIELD_VALUE.setToolTip('<h5>Value</h5>')
        self.Q_FIELD_VALUE.textChanged.connect(self.preview_html)
        
        # ADD ELEM, ATTR & VALUE TO LAYOUT        
        question_layout.addWidget(self.Q_FIELD_ELEM)
        question_layout.addWidget(self.Q_FIELD_ATTR)
        question_layout.addWidget(self.Q_FIELD_VALUE)
        
        ## ADD QUESTION TO ROW 4 RIGHT LAYOUT
        preview_right.addWidget(question_box)
        
        
        ###############################################
        # R.4.R.3           ANSWER
        ###############################################
        
        # LAYOUT
        answer_box    = QGroupBox('Answer')
        answer_layout = QHBoxLayout()
        answer_box.setLayout(answer_layout)

        # ELEM        
        self.A_FIELD_ELEM  = QLineEdit('all', self)
        self.A_FIELD_ELEM.setAlignment(Qt.AlignHCenter)
        self.A_FIELD_ELEM.setToolTip('<h5>Element:</h5><p><code>div<br />span</code></p>')
        self.A_FIELD_ELEM.textChanged.connect(self.preview_html)
        
        # ATTR        
        self.A_FIELD_ATTR  = QLineEdit('class', self)
        self.A_FIELD_ATTR.setAlignment(Qt.AlignHCenter)
        self.A_FIELD_ATTR.setToolTip('<h5>Attribute:</h5><p><code>id<br />class</code></p>') 
        self.A_FIELD_ATTR.textChanged.connect(self.preview_html)       
        
        # ATTR VALUE        
        self.A_FIELD_VALUE = QLineEdit('qDef', self)
        self.A_FIELD_VALUE.setAlignment(Qt.AlignHCenter)
        self.A_FIELD_VALUE.setToolTip('<h5>Value</h5>')
        self.A_FIELD_VALUE.textChanged.connect(self.preview_html)
        
        # ADD ELEM, ATTR & VALUE TO LAYOUT         
        answer_layout.addWidget(self.A_FIELD_ELEM)
        answer_layout.addWidget(self.A_FIELD_ATTR)
        answer_layout.addWidget(self.A_FIELD_VALUE)
        
        ## ADD ANSWER TO ROW 4 RIGHT LAYOUT        
        preview_right.addWidget(answer_box)
        
        
        ###############################################
        # R.4.R.4           IMAGES
        ###############################################
        
        # MAIN LAYOUT
        image_box      = QGroupBox('Images')
        image_layout   = QHBoxLayout()
        image_box.setLayout(image_layout)

        # PARENT LAYOUT        
        image_sub_layout  = QHBoxLayout()

        # CHILD LAYOUT
        image_fb_layout   = QVBoxLayout()
        image_dl_layout   = QVBoxLayout()
        image_attr_layout = QVBoxLayout()
        
        # F/B CHECKBOX
        self.I_BUTTON = QButtonGroup()
        self.I_FRONT  = QCheckBox('Front', self)
        self.I_BACK   = QCheckBox('Back', self)
        self.I_FRONT.setChecked(True)
        self.I_BUTTON.addButton(self.I_FRONT)
        self.I_BUTTON.addButton(self.I_BACK)

        # DL CHECKBOX
        self.DL_BUTTON = QButtonGroup()
        self.DL_YES  = QCheckBox('Download Media', self)
        self.DL_NO   = QCheckBox('Load Web Media', self)
        self.DL_NO.setChecked(True)
        self.DL_BUTTON.addButton(self.DL_YES)
        self.DL_BUTTON.addButton(self.DL_NO)

        # ATTR VALUE
        self.I_FIELD  = QLineEdit('data-srcset', self)
        self.I_FIELD.setAlignment(Qt.AlignHCenter)
        self.I_FIELD.setToolTip('<h5>Attribute:</h5><p><code>src<br />data-srcset</code></p>')
        self.I_FIELD.textChanged.connect(self.preview_html)       
        
        ### CHILD ###
        # ADD F/B CHECKBOX TO (LEFT) CHILD LAYOUT
        image_fb_layout.addWidget(self.I_FRONT)
        image_fb_layout.addWidget(self.I_BACK)

        # ADD DL CHECKBOX TO (MIDDLE) CHILD LAYOUT
        image_dl_layout.addWidget(self.DL_YES)
        image_dl_layout.addWidget(self.DL_NO)

        # ADD ATTR VALUE TO (RIGHT) CHILD LAYOUT
        image_attr_layout.addWidget(self.I_FIELD)

        ### PARENT ###
        # ADD CHILD LAYOUT TO PARENT LAYOUT
        image_sub_layout.addLayout(image_fb_layout)
        image_sub_layout.addLayout(image_dl_layout)
        image_sub_layout.addLayout(image_attr_layout)
        
        ### MAIN ###
        # ADD PARENT LAYOUT TO MAIN LAYOUT
        image_layout.addLayout(image_sub_layout)        
        
        ## ADD IMAGES TO ROW 4 RIGHT LAYOUT
        preview_right.addWidget(image_box)
        

        ###############################################
        # R.4.L           ROW 4 LEFT
        ###############################################
        
        ###############################################
        # R.4.L            PREVIEW
        ###############################################

        # LAYOUT
        preview_box      = QGroupBox('Preview')
        preview_layout   = QHBoxLayout()
        preview_box.setLayout(preview_layout)

        
        # BUILD HTML PREVIEW OF ELEMs, ATTRs & VALUEs
        selection = '''
<{s_e} {s_a}="{s_v}">
   <{q_e} {q_a}="{q_v}">Q1</{q_e}>
   <{a_e} {a_a}="{a_v}">A1</{a_e}>
   <img {i_a}="http://image1.png">
</{s_e}>
<{s_e} {s_a}="{s_v}">
   <{q_e} {q_a}="{q_v}">Q2</{q_e}>
   <{a_e} {a_a}="{a_v}">A2</{a_e}>
   <img {i_a}="http://image2.png">
</{s_e}>
        '''.format(s_e=self.S_FIELD_ELEM.text(), s_a=self.S_FIELD_ATTR.text(), s_v=self.S_FIELD_VALUE.text(), 
                    q_e=self.Q_FIELD_ELEM.text(), q_a=self.Q_FIELD_ATTR.text(), q_v=self.Q_FIELD_VALUE.text(), 
                    a_e=self.A_FIELD_ELEM.text(), a_a=self.A_FIELD_ATTR.text(), a_v=self.A_FIELD_VALUE.text(),
                    i_a=self.I_FIELD.text())

        # LABEL
        self.preview_selection = QLabel(selection)
        self.preview_selection.setTextFormat(Qt.PlainText)
        self.preview_selection.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                                font-weight: bold;
                                                font-size: 14px;''')
        
        # ADD LABEL TO LAYOUT
        preview_layout.addWidget(self.preview_selection)
        
        ## ADD IMAGES TO ROW 4 LEFT LAYOUT
        preview_left.addWidget(preview_box)
        
        
        ###############################################
        # R.5       ROW 5 RIGHT/LEFT LAYOUT
        ###############################################        
        
        # ROW 5 LAYOUT
        last_row   = QHBoxLayout()
        last_left  = QHBoxLayout()
        last_right = QHBoxLayout()
        
        # ADD R/L TO R.5 LAYOUT        
        last_row.addLayout(last_left)
        last_row.addLayout(last_right)
        
        ### ADD R.5 TO SETTINGS WIDGET        
        settings_layout.addLayout(last_row)
        
        
        ###############################################
        # R.5.L          ROW 5 LEFT
        ###############################################        

        ###############################################
        # R.5.L.1   STRIP FORMATTING ON IMPORT
        ###############################################        
        
        # LAYOUT
        strip_box      = QGroupBox('Strip Formatting')
        strip_layout   = QHBoxLayout()
        strip_box.setLayout(strip_layout)
        
        # CHECKBOX
        self.STRIP_FORMATTING  = QCheckBox('Remove Text Formatting', self)
        self.STRIP_FORMATTING.setChecked(False)
        
        # ADD CHECKBOX TO LAYOUT
        strip_layout.addWidget(self.STRIP_FORMATTING)
        
        # ADD STRIP FORMATTING TO ROW 5 LEFT LAYOUT
        last_left.addWidget(strip_box)
        
        
        ###############################################
        # R.5.L.2      THEME SELECTION
        ###############################################
        
        # LAYOUT
        theme_box      = QGroupBox('Theme')
        theme_layout   = QHBoxLayout()
        theme_box.setLayout(theme_layout)

        # CHECKBOX
        self.THEME  = QCheckBox('Dark Theme', self)
        self.THEME.setChecked(True)

        # ADD CHECKBOX TO LAYOUT
        theme_layout.addWidget(self.THEME)
        
        # ADD THEME SELECTION TO ROW 5 LEFT LAYOUT
        last_left.addWidget(theme_box)        
        
        
        ###############################################
        # R.5.R          ROW 5 RIGHT
        ###############################################
        
        ###############################################
        # R.5.R.1         RUN BUTTON
        ###############################################
        
        # LAYOUT
        run_box    = QGroupBox('Lets GO')
        run_layout = QHBoxLayout()
        run_box.setLayout(run_layout)

        # BUTTON
        self.HTML_RUN = QPushButton('RUN', self)
        self.HTML_RUN.clicked.connect(self.parse_html)
        
        # ADD BUTTON TO LAYOUT
        run_layout.addWidget(self.HTML_RUN)
        
        # ADD RUN BUTTON TO ROW 5 RIGHT LAYOUT
        last_right.addWidget(run_box)
        
        
        ###############################################
        # I.1          Deck Instructions
        ###############################################    

        # LAYOUT
        ins_deck_box      = QGroupBox('Deck')
        ins_deck_layout   = QHBoxLayout()
        ins_deck_box.setLayout(ins_deck_layout)

        # LABEL (NAME)
        self.INS_DECK = QLabel('Deck names follow normal syntax (e.g. sub decks are designated with "::"). Thus, "Phish::Is Awesome" will yield a deck named "Phish" with a subdeck "Is Awesome".')
        self.INS_DECK.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_DECK.setWordWrap(True)
        self.INS_DECK.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')

        # LABEL (TAGS)
        self.INS_TAGS = QLabel('Tags can be entered with or without commas.<br />So, "tag1, tag2" is the same as "tag1 tag2".')
        self.INS_TAGS.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_TAGS.setWordWrap(True)
        self.INS_TAGS.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
                                      
                
        # ADD LABEL TO LAYOUT
        ins_deck_layout.addWidget(self.INS_DECK)
        ins_deck_layout.addWidget(self.INS_TAGS)
        
        ### ADD DECK INSTRUCTIONS TO WIDGET
        instructions_layout.addWidget(ins_deck_box)
        
        
        ###############################################
        # I.2          HTML Instructions
        ###############################################
        
        # LAYOUT
        ins_html_box      = QGroupBox('HTML')
        ins_html_layout   = QVBoxLayout()
        ins_html_box.setLayout(ins_html_layout)

        # LABEL
        self.INS_HTML = QLabel('HTML can be either from a URL or a local file. Copy a URL from your browser and paste into the field, or browse for a local file. If a URL is pasted, and the dark layout is selected, a link will be insterted at the bottom right of the back card.')
        self.INS_HTML.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_HTML.setWordWrap(True)
        self.INS_HTML.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
        
        ins_html_layout.addWidget(self.INS_HTML)
        
        
        # URL 1
        ins_url1_box      = QGroupBox('Sample URL (CLICK BOX)')
        ins_url1_layout   = QHBoxLayout()
        ins_url1_box.setLayout(ins_url1_layout)
        self.INS_URL1 = QLabel('Copy to First Tab: http://quizlet.com/13696175/anatomy-and-physiology-study-guide-flash-cards/') 
        self.INS_URL1.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_URL1.mousePressEvent = self.url1_clipboard
        self.INS_URL1.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
        
        ins_url1_layout.addWidget(self.INS_URL1)
        
        # URL 2
        ins_url2_box      = QGroupBox('Sample URL w. Images (CLICK BOX)')
        ins_url2_layout   = QHBoxLayout()
        ins_url2_box.setLayout(ins_url2_layout)
        self.INS_URL2 = QLabel('Copy to First Tab: http://quizlet.com/2621787/histology-lab-photo-quiz-flash-cards/') 
        self.INS_URL2.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_URL2.mousePressEvent = self.url2_clipboard
        self.INS_URL2.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
        
        ins_url2_layout.addWidget(self.INS_URL2)
       
        
        
        ### ADD HTML INSTRUCTIONS TO WIDGET
        instructions_layout.addWidget(ins_html_box)
        instructions_layout.addWidget(ins_url1_box)
        instructions_layout.addWidget(ins_url2_box)
        
        
        ###############################################
        # I.3        SELECTORS Instructions
        ###############################################
        
        # LAYOUT
        ins_sele_box      = QGroupBox('Selection')
        ins_sele_layout   = QVBoxLayout()
        ins_sele_box.setLayout(ins_sele_layout)
        
        # LABEL
        self.INS_SELE = QLabel('The default setting are for Quizlet, so that will work straight out of the box. The HTML preview on the first tab is fairly explanatory, but for a thorough explanation please see the <a href="http://www.crummy.com/software/BeautifulSoup/bs3/documentation.html">BeautifulSoup documentation</a>. Note: For whatever reason Anki uses version 3. The fields with "all" will look in every element for the associated class or id, but you can change this as you please.')
        self.INS_SELE.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_SELE.setWordWrap(True)
        self.INS_SELE.setOpenExternalLinks(True)
        self.INS_SELE.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
        
        ins_sele_layout.addWidget(self.INS_SELE)
        
        ### ADD SELECTION INSTRUCTIONS TO WIDGET
        instructions_layout.addWidget(ins_sele_box)
        
        
        ###############################################
        # I.4        IMAGES Instructions
        ###############################################
        
        # LAYOUT
        ins_img_box      = QGroupBox('Images')
        ins_img_layout   = QVBoxLayout()
        ins_img_box.setLayout(ins_img_layout)
        
        # LABEL
        self.INS_IMG = QLabel('Also fairly explanatory. Select if you want the image on the front or back card, and also if you would like the image to be downloaded to the Anki media folder or if it should be loaded remotely.')
        self.INS_IMG.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_IMG.setWordWrap(True)
        self.INS_IMG.setOpenExternalLinks(True)
        self.INS_IMG.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
        
        ins_img_layout.addWidget(self.INS_IMG)
        
        ### ADD SELECTION INSTRUCTIONS TO WIDGET
        instructions_layout.addWidget(ins_img_box)
        
        
        ###############################################
        # I.5     FORMAT/THEME Instructions
        ###############################################
        
        # LAYOUT
        ins_theme_box      = QGroupBox('Format and Theme')
        ins_theme_layout   = QVBoxLayout()
        ins_theme_box.setLayout(ins_theme_layout)
        
        # LABEL
        self.INS_THEME = QLabel('If you would like to strip formatting from the HTML then check the box. So, if text had new lines and <b>bold text</b> in the HTML then it would now be one line without bolded text. The dark theme is exactly what you think it is, but it has some javascript included to handle images better on desktop and mobile.')
        self.INS_THEME.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_THEME.setWordWrap(True)
        self.INS_THEME.setOpenExternalLinks(True)
        self.INS_THEME.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
        
        ins_theme_layout.addWidget(self.INS_THEME)
        
        ### ADD THEME INSTRUCTIONS TO WIDGET
        instructions_layout.addWidget(ins_theme_box)
        
        
        ###############################################
        # I.6     FORMAT/THEME Instructions
        ###############################################
        
        # LAYOUT
        ins_issues_box      = QGroupBox('Help')
        ins_issues_layout   = QVBoxLayout()
        ins_issues_box.setLayout(ins_issues_layout)
        
        # LABEL
        self.INS_HELP = QLabel('If you run into any issues please post them at the <a href="https://github.com/DrLulz/HTML-2-ANKI">GitHub repository</a>.')
        self.INS_HELP.setAlignment(Qt.AlignHCenter|Qt.AlignVCenter)
        self.INS_HELP.setWordWrap(True)
        self.INS_HELP.setOpenExternalLinks(True)
        self.INS_HELP.setStyleSheet('''font-family: "Courier New", Courier, monospace;
                                      font-size: 10px;''')
        
        ins_issues_layout.addWidget(self.INS_HELP)
        
        ### ADD THEME INSTRUCTIONS TO WIDGET
        instructions_layout.addWidget(ins_issues_box)
        
        
        
        
        # TAB WIDGET
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        tab_widget.addTab(settings_widget,'Settings')     
        tab_widget.addTab(instructions_widget,'Instructions')
        
        
        ###############################################
        #               STYLE & SHOW
        ###############################################

        self.setStyleSheet('''QToolTip {
                                 font-size: 16px;
                                 border: 2px solid darkblue;
                                 padding: 3px;
                                 opacity: 300;                                
                                 }''')
        
        self.setGeometry(0, 10, 800, 0)
        #self.resize(480, 600)
        self.setWindowTitle('HTML 2 ANKI')
        self.center_ui()  
        self.show()
        
        #showInfo(self.THEME)
        #QDesktopServices.openUrl(QUrl('file:///%s' % dirname))
        


    def url1_clipboard(self, event):
        clipboard = QApplication.clipboard()
        clipboard.setText('http://quizlet.com/13696175/anatomy-and-physiology-study-guide-flash-cards/')
        self.HTML_FIELD.setText('http://quizlet.com/13696175/anatomy-and-physiology-study-guide-flash-cards/')
        
        
    def url2_clipboard(self, event):
        clipboard = QApplication.clipboard()
        clipboard.setText('http://quizlet.com/2621787/histology-lab-photo-quiz-flash-cards/')
        self.HTML_FIELD.setText('http://quizlet.com/2621787/histology-lab-photo-quiz-flash-cards/')



    def preview_html(self):

        '''Update HTML preview when user changes text field'''
        
        selection = '''
<{s_e} {s_a}="{s_v}">
   <{q_e} {q_a}="{q_v}">Q1</{q_e}>
   <{a_e} {a_a}="{a_v}">A1</{a_e}>
   <img {i_a}="http://image1.png">
</{s_e}>
<{s_e} {s_a}="{s_v}">
   <{q_e} {q_a}="{q_v}">Q2</{q_e}>
   <{a_e} {a_a}="{a_v}">A2</{a_e}>
   <img {i_a}="http://image2.png">
</{s_e}>
        '''.format(s_e=self.S_FIELD_ELEM.text(), s_a=self.S_FIELD_ATTR.text(), s_v=self.S_FIELD_VALUE.text(), 
                q_e=self.Q_FIELD_ELEM.text(), q_a=self.Q_FIELD_ATTR.text(), q_v=self.Q_FIELD_VALUE.text(), 
                a_e=self.A_FIELD_ELEM.text(), a_a=self.A_FIELD_ATTR.text(), a_v=self.A_FIELD_VALUE.text(),
                i_a=self.I_FIELD.text())

        self.preview_selection.setText(selection)
        
        
 
    def center_ui(self):
        resolution = QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 20) - (self.frameSize().height() / 20))
                  

                  
    def make_cards(self, terms):
        
        title = self.DECK_FIELD.text()
        img_side = self.I_BUTTON.checkedButton().text()
        tags = re.split(' |, ', self.TAGS_FIELD.text())
        model_name = 'HTML 2 ANKI'
        
        #log.info(terms)
        
        # MAKE DECK
        deck = mw.col.decks.get(mw.col.decks.id(title))
        
        # MAKE MODEL IF IT DOESN'T EXIST
        if self.THEME.isChecked():
            if not mw.col.models.byName('Basic (HTML 2 ANKI DARK)') is None:
                model = mw.col.models.byName('Basic (HTML 2 ANKI DARK)')
            else:
                model = dark_theme(model_name, mw.col)
        else:
            if not mw.col.models.byName('Basic (HTML 2 ANKI)') is None:
                model = mw.col.models.byName('Basic (HTML 2 ANKI)')
            else:
                model = basic_theme(model_name, mw.col)
            
        # ASSIGN MODEL TO DECK
        mw.col.decks.select(deck['id'])
        mw.col.decks.get(deck)['mid'] = model['id']
        mw.col.decks.save(deck)

        # ASSIGN DECK TO MODEL
        mw.col.models.setCurrent(model)
        mw.col.models.current()['did'] = deck['id']
        mw.col.models.save(model)
        

        # ITERATE CARDS
        for term in terms:            
            card = mw.col.newNote()
            if not term['question'] is None:
                card['Front'] = u''.join(unicode(i) for i in term['question'])
            if not term['answer'] is None:
                card['Back']  = u''.join(unicode(i) for i in term['answer'])
            if not term['image'] is None:
                card[img_side] += u'<img src="%s">' % term['image']
                mw.app.processEvents()

            card['http'] = u''.join(unicode(i) for i in term['url'])
            card.tags = filter(None, tags)
            mw.col.addNote(card)

        mw.col.reset()
        mw.reset()
        
        return terms
        
    
    def parse_html(self):
        
        # DID USER ENTER A DECK NAME?
        if (self.DECK_FIELD.text() == ''):
            self.FEEDBACK.setText('Assign Deck Name')
            return
        # DID USER ENTER HTML?
        elif (self.HTML_FIELD.text()) == '':
            self.FEEDBACK.setText('Designate URL or File')
            return
        else:
            pass
        
        # DEFINE VARIABLES
        self.url = self.HTML_FIELD.text()
        s_attr   = self.S_FIELD_ATTR.text()
        q_attr   = self.Q_FIELD_ATTR.text()
        a_attr   = self.A_FIELD_ATTR.text()
        s_value  = self.S_FIELD_VALUE.text()
        q_value  = self.Q_FIELD_VALUE.text()
        a_value  = self.A_FIELD_VALUE.text()
        
        # DETERMINE HTML SOURCE
        if re.match('^http', self.url):
            req      = urllib2.Request(self.url)
            response = urllib2.urlopen(req)
            html     = response.read()
        else:
            loc_html = open(self.url, 'r')
            html     = loc_html.read()
            
        
        # MAP 'all' --> 'True' TO GET ALL ELEMENTS
        # The word 'all' is more intuitive to end users
        if self.S_FIELD_ELEM.text() == 'all':
            s_elem = True
        else:
            s_elem = self.S_FIELD_ELEM.text()
            
        if self.Q_FIELD_ELEM.text() == 'all':
            q_elem = True
        else:
            q_elem = self.Q_FIELD_ELEM.text()
            
        if self.A_FIELD_ELEM.text() == 'all':
            a_elem = True
        else:
            a_elem = self.A_FIELD_ELEM.text()


        # MAKE SOUP & SELECT PARENT ELEMENTS FOR Q/A
        soup    = bs(html)
        qas     = soup.findAll(s_elem, { s_attr : re.compile(r'\b%s\b' % s_value) })
        
        try:
            title = soup.find('title').text
        except AttributeError:
            pass

        self.results = []
        for qa in qas:
            
            # DEFAULT VALUES
            question, answer, image = (None,)*3
            data = {'question': None, 'answer': None, 'image': None, 'url': None}
            
            data['url'] = self.url
            

            # GET QUESTION
            try:
                if not self.STRIP_FORMATTING.isChecked():
                    question = qa.find(q_elem, attrs={ q_attr : re.compile(r'\b%s\b' % q_value) }).contents
                else:
                    question = qa.find(q_elem, attrs={ q_attr : re.compile(r'\b%s\b' % q_value) }).text
            except AttributeError:
                pass
            if question is not None:
                data['question'] = question
            

            # GET ANSWER
            try:
                if not self.STRIP_FORMATTING.isChecked():
                    answer = qa.find(a_elem, attrs={ a_attr : re.compile(r'\b%s\b' % a_value) }).contents
                else:
                    answer = qa.find(a_elem, attrs={ a_attr : re.compile(r'\b%s\b' % a_value) }).text
            except AttributeError:
                pass
            if answer is not None:
                data['answer'] = answer
                

            # GET IMAGE
            try:
                image = qa.find('img')[self.I_FIELD.text()]
            except (TypeError, AttributeError):
                pass
            if image is not None:
                # DOWNLOAD YES/NO
                if self.DL_NO.isChecked():
                    data['image'] = image                    
                else:
                    data['image'] = self.get_img(image)
                

            # FILTER EMPTY CARDS & ADD TO RESULTS
            if bool([i for i in data.values() if i != None]):
                self.results.append(data)
                            
        
        self.make_cards(self.results)

        h = HTMLParser()
        feedback = h.unescape(title)
        self.FEEDBACK.setText(feedback)
        #log.info(feedback)

        
        
    def local_file(self):
        # LOAD LOCAL HTML FILE PATH
        path = QFileDialog.getOpenFileName(self, 'Select HTML File', os.getcwd()) #(self, 'Select HTML File', '/home')
        self.HTML_FIELD.setText(path)

        
        
    def get_img(self, url):
        # DOWNLOAD IMG TO MEDIA FOLDER & RETURN NAME
        media_dir = re.sub("(?i)\.(anki2)$", ".media", mw.col.path)
        img_name  = url.split('/')[-1]
        img_path  = os.path.join(media_dir, img_name)
        urllib.urlretrieve(url, img_path)
        
        return img_name



def run_HTML_2_ANKI():
    global __window
    __window = UI()


# ANKI MENU ITEM
action = QAction("HTML 2 Anki", mw)
mw.connect(action, SIGNAL("triggered()"), run_HTML_2_ANKI)
mw.form.menuTools.addAction(action)