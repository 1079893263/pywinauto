# GUI Application automation and testing library
# Copyright (C) 2006-2017 Mark Mc Mahon and Contributors
# https://github.com/pywinauto/pywinauto/graphs/contributors
# http://pywinauto.readthedocs.io/en/latest/credits.html
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of pywinauto nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Basic wrapping of UI Automation elements"""

from __future__ import unicode_literals
from __future__ import print_function

import six

from .. import backend
from ..base_wrapper import BaseWrapper
from ..base_wrapper import BaseMeta

from ..linux.atspi_element_info import AtspiElementInfo
from ..linux.atspi_objects import AtspiStateSet, AtspiAccessible

from Xlib import Xatom
from Xlib.display import Display

# region PATTERNS


# =========================================================================
class AtspiMeta(BaseMeta):

    """Metaclass for UiaWrapper objects"""
    control_type_to_cls = {}

    def __init__(cls, name, bases, attrs):
        """Register the control types"""

        BaseMeta.__init__(cls, name, bases, attrs)

    @staticmethod
    def find_wrapper(element):
        # TODO find derived wrapper class and return it
        return AtspiWrapper


# =========================================================================
@six.add_metaclass(AtspiMeta)
class AtspiWrapper(BaseWrapper):

    """
    Default wrapper for User Interface Automation (UIA) controls.

    All other UIA wrappers are derived from this.

    This class wraps a lot of functionality of underlying UIA features
    for working with windows.

    Most of the methods apply to every single element type. For example
    you can click() on any element.
    """

    _control_types = []

    # ------------------------------------------------------------
    def __new__(cls, element_info):
        """Construct the control wrapper"""
        return super(AtspiWrapper, cls)._create_wrapper(cls, element_info, AtspiWrapper)

    # -----------------------------------------------------------
    def __init__(self, element_info):
        """
        Initialize the control

        * **element_info** is either a valid UIAElementInfo or it can be an
          instance or subclass of UIAWrapper.
        If the handle is not valid then an InvalidWindowHandle error
        is raised.
        """
        BaseWrapper.__init__(self, element_info, backend.registry.backends['atspi'])
        self.state_set = self.element_info.get_state_set()

    # ------------------------------------------------------------
    def __hash__(self):
        """Return a unique hash value based on the element's Runtime ID"""
        return hash(self.element_info.runtime_id)

    # ------------------------------------------------------------

    def set_keyboard_focus(self):
        """Set the focus to this element"""
        self.element_info.component.grab_focus("screen")

    def set_window_focus(self, pid):
        display = Display()
        root = display.screen().root

        def top_level_set_focus_by_pid(pid, window, indent):
            children = window.query_tree().children
            for w in children:
                if window.get_wm_class() is not None:
                    if window.get_full_property(display.get_atom("_NET_WM_PID"), Xatom.CARDINAL).value[0] == pid:
                        window.raise_window()

                top_level_set_focus_by_pid(pid, w, indent + '-')

        top_level_set_focus_by_pid(pid, root, '-')

    def set_focus(self):
        if self.parent() == self.root():
            self.set_window_focus(self.element_info.process_id)
        else:
            # TODO add check is focus set
            self.set_keyboard_focus()

    def get_states(self):
        return self.state_set.get_states()


backend.register('atspi', AtspiElementInfo, AtspiWrapper)
