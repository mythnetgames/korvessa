"""
Django forms for Kowloon character creation and account registration.

Extends Evennia's default forms to add custom stat system, name structure,
and Cloudflare Turnstile verification.
"""

from django import forms
from evennia.web.website.forms import (
    CharacterForm as EvenniaCharacterForm,
    AccountForm as EvenniaAccountForm
)


# Constants for character stat system
STAT_TOTAL_POINTS = 68  # Total points available for all stats
STAT_MIN = 1
STAT_MAX = 10

# Stats with their max values
STATS = {
    'smarts': {'max': 10, 'label': 'Smarts', 'help': 'Logic, memory, reasoning'},
    'body': {'max': 10, 'label': 'Body', 'help': 'Physical strength and health'},
    'willpower': {'max': 10, 'label': 'Willpower', 'help': 'Mental fortitude and determination'},
    'dexterity': {'max': 10, 'label': 'Dexterity', 'help': 'Agility and hand coordination'},
    'edge': {'max': 10, 'label': 'Edge', 'help': 'Luck, cunning, and instinct'},
    'empathy': {'max': 6, 'label': 'Empathy', 'help': 'Understanding and compassion'},
    'reflexes': {'max': 10, 'label': 'Reflexes', 'help': 'Speed and reaction time'},
    'technique': {'max': 10, 'label': 'Technique', 'help': 'Skill and precision'},
}

SEX_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('ambiguous', 'Ambiguous'),
]


class CharacterForm(EvenniaCharacterForm):
    """
    Extends Evennia's default CharacterForm with custom stats and name structure.
    
    Stat System:
    - Smarts: Logic, memory, reasoning
    - Body: Physical strength and health
    - Willpower: Mental fortitude and determination
    - Dexterity: Agility and hand coordination
    - Edge: Luck, cunning, and instinct
    - Empathy: Understanding and compassion (max 6)
    - Reflexes: Speed and reaction time
    - Technique: Skill and precision
    
    Total points: 68
    """
    
    # Name fields (split from db_key)
    first_name = forms.CharField(
        max_length=30,
        min_length=2,
        label="First Name",
        help_text="Your character's first name (2-30 characters)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        min_length=2,
        label="Last Name",
        help_text="Your character's last name (2-30 characters)",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    
    # Sex/Gender
    sex = forms.ChoiceField(
        choices=SEX_CHOICES,
        initial='ambiguous',
        label="Sex",
        help_text="Biological sex presentation",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Custom Stats
    smarts = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=10,
        initial=8,
        label="Smarts",
        help_text="Logic, memory, reasoning (1-10)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'smarts',
        })
    )
    
    body = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=10,
        initial=8,
        label="Body",
        help_text="Physical strength and health (1-10)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'body',
        })
    )
    
    willpower = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=10,
        initial=8,
        label="Willpower",
        help_text="Mental fortitude and determination (1-10)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'willpower',
        })
    )
    
    dexterity = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=10,
        initial=8,
        label="Dexterity",
        help_text="Agility and hand coordination (1-10)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'dexterity',
        })
    )
    
    edge = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=10,
        initial=8,
        label="Edge",
        help_text="Luck, cunning, and instinct (1-10)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'edge',
        })
    )
    
    empathy = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=6,
        initial=4,
        label="Empathy",
        help_text="Understanding and compassion (1-6)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'empathy',
        })
    )
    
    reflexes = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=10,
        initial=8,
        label="Reflexes",
        help_text="Speed and reaction time (1-10)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'reflexes',
        })
    )
    
    technique = forms.IntegerField(
        min_value=STAT_MIN,
        max_value=10,
        initial=8,
        label="Technique",
        help_text="Skill and precision (1-10)",
        widget=forms.NumberInput(attrs={
            'class': 'form-control stat-field',
            'data-stat': 'technique',
        })
    )
    
    class Meta(EvenniaCharacterForm.Meta):
        # Extend parent's fields with our custom fields
        fields = ('first_name', 'last_name', 'sex', 'desc', 'smarts', 'body', 'willpower', 'dexterity', 'edge', 'empathy', 'reflexes', 'technique')
    
    def clean_first_name(self):
        """Validate first name format."""
        import re
        name = self.cleaned_data.get('first_name', '').strip()
        
        if not re.match(r"^[a-zA-Z][a-zA-Z\-']*[a-zA-Z]$", name):
            raise forms.ValidationError(
                "Name must start and end with a letter, and contain only letters, hyphens, and apostrophes."
            )
        
        return name
    
    def clean_last_name(self):
        """Validate last name format."""
        import re
        name = self.cleaned_data.get('last_name', '').strip()
        
        if not re.match(r"^[a-zA-Z][a-zA-Z\-']*[a-zA-Z]$", name):
            raise forms.ValidationError(
                "Name must start and end with a letter, and contain only letters, hyphens, and apostrophes."
            )
        
        return name
    
    def clean(self):
            """
            Validate that custom stats total exactly 68 points.
            """
            cleaned_data = super().clean()
            stat_names = ['smarts', 'body', 'willpower', 'dexterity', 'edge', 'empathy', 'reflexes', 'technique']
            stats = [int(cleaned_data.get(name, 0)) for name in stat_names]
            total = sum(stats)
            if total != STAT_TOTAL_POINTS:
                raise forms.ValidationError(
                    f"Stats must total exactly {STAT_TOTAL_POINTS} points. Current total: {total} points."
                )
            return cleaned_data


class TurnstileAccountForm(EvenniaAccountForm):
    """
    Extends Evennia's AccountForm with Cloudflare Turnstile verification.
    
    Adds a hidden field to capture the Turnstile response token,
    which is validated server-side in the view.
    
    Overrides email field to make it required (critical for password resets).
    """
    
    # Hidden field to store Turnstile response token
    # This is populated by the Turnstile JavaScript widget
    cf_turnstile_response = forms.CharField(
        widget=forms.HiddenInput(),
        required=True,
        error_messages={
            'required': 'CAPTCHA verification is required. Please complete the verification.'
        }
    )
    
    def __init__(self, *args, **kwargs):
        """Override email field to make it required."""
        super().__init__(*args, **kwargs)
        # Make email required and update help text
        self.fields['email'].required = True
        self.fields['email'].help_text = "A valid email address. Required for login and password resets."
        self.fields['email'].error_messages = {
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.'
        }
    
    def clean_email(self):
        """
        Validate that the email address is unique (case-insensitive).
        
        This is critical because Evennia's email_login contrib allows users
        to log in with their email address, so duplicate emails could cause
        authentication conflicts.
        """
        from evennia.accounts.models import AccountDB
        
        email = self.cleaned_data.get('email', '').strip()
        
        if not email:
            raise forms.ValidationError("Email address is required.")
        
        # Check for existing account with this email (case-insensitive)
        if AccountDB.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists. "
                "If you forgot your password, use the password reset link."
            )
        
        return email
    
    def clean_username(self):
        """
        Validate username uniqueness (case-insensitive).
        
        This adds an explicit check in addition to the parent form's validation
        to provide clearer error messages and ensure consistency.
        """
        from evennia.accounts.models import AccountDB
        
        username = self.cleaned_data.get('username', '').strip()
        
        if not username:
            raise forms.ValidationError("Username is required.")
        
        # Check for existing account with this username (case-insensitive)
        if AccountDB.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "An account with this username already exists. "
                "Please choose a different username."
            )
        
        return username
    
    class Meta(EvenniaAccountForm.Meta):
        # Extend parent's fields with Turnstile response
        fields = EvenniaAccountForm.Meta.fields + ('cf_turnstile_response',)

