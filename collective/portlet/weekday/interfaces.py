from zope.interface import Interface
from zope import schema

from collective.portlet.weekday import PloneMessageFactory as _
from plone.app.textfield import RichText
from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Weekday portlet" this interface must be its layer
    """

class IWeekDayContent(Interface):
    """
    This interface defines the weekdays record on the registry
    """
    
    mondayActive = schema.Bool(
        title=_(u"monday_active", default=u"Active"),
        required=False)
    
    tuesdayActive = schema.Bool(
        title=_(u"tuesday_active", default=u"Active"),
        default=False,
        required=False)
    
    wednesdayActive = schema.Bool(
        title=_(u"wednesday_active", default=u"Active"),
        default=False,
        required=False)
    
    thursdayActive = schema.Bool(
        title=_(u"thursday_active", default=u"Active"),
        default=False,
        required=False)
    
    fridayActive = schema.Bool(
        title=_(u"friday_active", default=u"Active"),
        default=False,
        required=False)
    
    saturdayActive = schema.Bool(
        title=_(u"saturday_active", default=u"Active"),
        default=False,
        required=False)
    
    sundayActive = schema.Bool(
        title=_(u"sunday_active", default=u"Active"),
        default=False,
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
    
    no_event = RichText(
        title=_(u"no_event", default=u"No Events"),
        description=_(u"sunday_content", default=u"Content to display when there are no events."),
        required=False)
    
    