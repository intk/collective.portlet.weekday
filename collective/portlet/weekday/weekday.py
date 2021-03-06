import random

from AccessControl import getSecurityManager

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
#from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue

from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFCore.utils import getToolByName
from datetime import date
from DateTime import DateTime
import time

from collective.portlet.weekday import PloneMessageFactory as _

from Acquisition import aq_inner
from collective.portlet.weekday.interfaces import IWeekDayContent
from z3c.form import form, field, button, group
from plone.app.z3cform.layout import wrap_form
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFPlone.utils import getFSVersionTuple

PLONE5 = getFSVersionTuple()[0] >= 5

if PLONE5:
    base_AddForm = base.AddForm
    base_EditForm = base.EditForm
else:
    from plone.app.portlets.browser.z3cformhelper import AddForm as base_AddForm  # noqa
    from plone.app.portlets.browser.z3cformhelper import EditForm as base_EditForm  # noqa
    from z3c.form import field

class IWeekDayPortlet(IPortletDataProvider):
    """A portlet which renders content depending on the day of the week
    """
    header = schema.TextLine(
        title=_(u"Title", default=u"Title"),
        description=_(u"portlet_title", default=u"Title of the portlet. Leave empty to display the current date."),
        required=False)
    
    monday = RichText(
        title=_(u"monday", default=u"Monday"),
        description=_(u"monday_content", default=u"Content to display on Mondays"),
        required=False)
    
    tuesday = RichText(
        title=_(u"tuesday", default=u"Tuesday"),
        description=_(u"tuesday_content", default=u"Content to display on Tuesdays"),
        required=False)
    
    wednesday = RichText(
        title=_(u"wednesday", default=u"Wednesday"),
        description=_(u"wednesday_content", default=u"Content to display on Wednesdays"),
        required=False)
    
    thursday = RichText(
        title=_(u"thursday", default=u"Thursday"),
        description=_(u"thursday_content", default=u"Content to display on Thursdays"),
        required=False)
    
    friday = RichText(
        title=_(u"friday", default=u"Friday"),
        description=_(u"friday_content", default=u"Content to display on Fridays"),
        required=False)
    
    saturday = RichText(
        title=_(u"saturday", default=u"Saturday"),
        description=_(u"saturday_content", default=u"Content to display on Saturdays"),
        required=False)
    
    sunday = RichText(
        title=_(u"sunday", default=u"Sunday"),
        description=_(u"sunday_content", default=u"Content to display on Sundays"),
        required=False)

class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IWeekDayPortlet)
    
    header = u''
    monday = u'' 
    tuesday = u''
    wednesday = u''
    thursday = u''
    friday = u''
    saturday = u''
    sunday = u''
    
    def __init__(self, header = u'', monday = u'', tuesday = u'', wednesday = u'', thursday = u'', friday = u'', saturday = u'', sunday = u''):
        self.header = header
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave or
        static string if title not defined.
        """
        return self.header or _(u'weekday_portlet', default=u"Weekday Portlet")

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('weekday.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return True
    
    def css_class(self):
        return "portlet-weekday"
    
    def getTitle(self):
        if self.data.header:
            return self.data.header
        else:
            return DateTime().strftime("%A %d %B %Y")
    
    def getTodayContent(self):
        weekday = DateTime().strftime("%u")
        if weekday == '1':
            return self.transformed(self.data.monday)
        elif weekday == '2':
            return self.transformed(self.data.tuesday)
        elif weekday == '3':
            return self.transformed(self.data.wednesday)
        elif weekday == '4':
            return self.transformed(self.data.thursday)
        elif weekday == '5':
            return self.transformed(self.data.friday)
        elif weekday == '6':
            return self.transformed(self.data.saturday)
        elif weekday == '7':
            return self.transformed(self.data.sunday)
        
    def transformed(self, text, mt='text/x-html-safe'):
        """Use the safe_html transform to protect text output. This also
            ensures that resolve UID links are transformed into real links.
        """
        orig = text
        context = aq_inner(self.context)
        if isinstance(orig, RichTextValue):
            orig = orig.raw

        if not isinstance(orig, unicode):
            # Apply a potentially lossy transformation, and hope we stored
            # utf-8 text. There were bugs in earlier versions of this portlet
            # which stored text directly as sent by the browser, which could
            # be any encoding in the world.
            orig = unicode(orig, 'utf-8', 'ignore')
            logger.warn("Static portlet at %s has stored non-unicode text. "
                "Assuming utf-8 encoding." % context.absolute_url())

        # Portal transforms needs encoded strings
        orig = orig.encode('utf-8')

        transformer = getToolByName(context, 'portal_transforms')
        transformer_context = context
        if hasattr(self, '__portlet_metadata__'):
            if ('category' in self.__portlet_metadata__ and
                    self.__portlet_metadata__['category'] == 'context'):
                assignment_context_path = self.__portlet_metadata__['key']
                assignment_context = context.unrestrictedTraverse(assignment_context_path)
                transformer_context = assignment_context
        data = transformer.convertTo(mt, orig,
                                     context=transformer_context, mimetype='text/html')
        result = data.getData()
        if result:
            if isinstance(result, str):
                return unicode(result, 'utf-8')
            return result
        return None

class AddForm(base_AddForm):
    #form_fields = form.Fields(IWeekDayPortlet)
    
    if PLONE5:
        schema = IWeekDayPortlet
    else:
        fields = field.Fields(IWeekDayPortlet)

    """form_fields['monday'].custom_widget = WYSIWYGWidget
    form_fields['tuesday'].custom_widget = WYSIWYGWidget
    form_fields['wednesday'].custom_widget = WYSIWYGWidget
    form_fields['thursday'].custom_widget = WYSIWYGWidget
    form_fields['friday'].custom_widget = WYSIWYGWidget
    form_fields['saturday'].custom_widget = WYSIWYGWidget
    form_fields['sunday'].custom_widget = WYSIWYGWidget"""
    label = _(u"Add week day portlet")
    description = _(u"This portlet renders content depending on the day of the week.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base_EditForm):
    #form_fields = form.Fields(IWeekDayPortlet)

    if PLONE5:
        schema = IWeekDayPortlet
    else:
        fields = field.Fields(IWeekDayPortlet)

    """form_fields['monday'].custom_widget = WYSIWYGWidget
    form_fields['tuesday'].custom_widget = WYSIWYGWidget
    form_fields['wednesday'].custom_widget = WYSIWYGWidget
    form_fields['thursday'].custom_widget = WYSIWYGWidget
    form_fields['friday'].custom_widget = WYSIWYGWidget
    form_fields['saturday'].custom_widget = WYSIWYGWidget
    form_fields['sunday'].custom_widget = WYSIWYGWidget"""

    label = _(u"Edit week day portlet")
    description = _(u"This portlet renders content depending on the day of the week.")


class MondayGroup(group.Group):
    label = u'Monday'
    fields = field.Fields(IWeekDayContent).select(
        'mondayActive', 'monday')
    
class TuesdayGroup(group.Group):
    label = u'Tuesday'
    fields = field.Fields(IWeekDayContent).select(
        'tuesdayActive', 'tuesday')
    
class WednesdayGroup(group.Group):
    label = u'Wednesday'
    fields = field.Fields(IWeekDayContent).select(
        'wednesdayActive', 'wednesday')
    
class ThursdayGroup(group.Group):
    label = u'Thursday'
    fields = field.Fields(IWeekDayContent).select(
        'thursdayActive', 'thursday')
    
class FridayGroup(group.Group):
    label = u'Friday'
    fields = field.Fields(IWeekDayContent).select(
        'fridayActive', 'friday')
    
class SaturdayGroup(group.Group):
    label = u'Saturday'
    fields = field.Fields(IWeekDayContent).select(
        'saturdayActive', 'saturday')
    
class SundayGroup(group.Group):
    label = u'Sunday'
    fields = field.Fields(IWeekDayContent).select(
        'sundayActive', 'sunday')

class NoEventGroup(group.Group):
    label = u'No events'
    fields = field.Fields(IWeekDayContent).select('no_event')


class WeekDayForm(RegistryEditForm):
    """
    This is a view with a form to fill a body text that depends on the weekday.
    """
    schema = IWeekDayContent
    groups = (
        MondayGroup,
        TuesdayGroup,
        WednesdayGroup,
        ThursdayGroup,
        FridayGroup,
        SaturdayGroup,
        SundayGroup,
        NoEventGroup)
    label = u"Weekday specific messages"
    description = u"Enter messages to replace today's events on each weekday. You can also add a message for days in which there are no events."
    
    
    def updateFields(self):
        super(WeekDayForm, self).updateFields()
        self.groups[0].fields['monday'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.groups[1].fields['tuesday'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.groups[2].fields['wednesday'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.groups[3].fields['thursday'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.groups[4].fields['friday'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.groups[5].fields['saturday'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.groups[6].fields['sunday'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
        self.groups[7].fields['no_event'].widgetFactory[INPUT_MODE] = WysiwygFieldWidget
    
    @button.buttonAndHandler(u'save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(u"Changes saved.", "info")
        
    @button.buttonAndHandler(u'cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(u"Edit cancelled.", "info")
        self.request.response.redirect("%s" % self.context.absolute_url())
    
    """ 
    @button.buttonAndHandler(u'Save')
    def handleSave(self, action):
        data, errors = self.extractData()
        registry = getUtility(IRegistry)
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.monday'] = data['monday']
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.tuesday'] = data['tuesday']
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.wednesday'] = data['wednesday']
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.thursday'] = data['thursday']
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.friday'] = data['friday']
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.saturday'] = data['saturday']
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.sunday'] = data['sunday']
        registry['plonetheme.arnolfini.interfaces.IWeekDayContent.no_event'] = data['no_event']
        self.status = u"Your settings have been saved successfully."
    """

WeekDayFormView = wrap_form(WeekDayForm)


