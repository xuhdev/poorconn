{{ fullname | escape | underline}}

{% set simulation_functions =
      'close_upon_acceptance',
      'delay_before_sending',
      'delay_before_sending_once',
      'delay_before_sending_upon_acceptance',
      'delay_before_sending_upon_acceptance_once'
%}

.. automodule:: {{ fullname }}

   {% block attributes %}
   {% if attributes %}
   .. rubric:: {{ _('Module Attributes') }}

   .. autosummary::
      :toctree:
   {% for item in attributes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block functions %}
   {% if functions %}
   .. rubric:: {{ _('Simulation Functions') }}

   .. autosummary::
      :toctree:
   {% for item in simulation_functions %}
      {{ item }}
   {%- endfor %}

   .. rubric:: {{ _('Other Functions') }}

   .. autosummary::
      :toctree:
   {% for item in functions %}
     {% if item not in simulation_functions %}
      {{ item }}
     {% endif %}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block classes %}
   {% if classes %}
   .. rubric:: {{ _('Classes') }}

   .. autosummary::
      :toctree:
      :template: poorconn-class.rst
   {% for item in classes %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

   {% block exceptions %}
   {% if exceptions %}
   .. rubric:: {{ _('Exceptions') }}

   .. autosummary::
      :toctree:
   {% for item in exceptions %}
      {{ item }}
   {%- endfor %}
   {% endif %}
   {% endblock %}

{% block modules %}
{% if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
   :template: poorconn-module.rst
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}
