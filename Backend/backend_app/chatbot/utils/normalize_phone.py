"""
Phone Number Normalizer for Chatbot/Co-Pilot Module

Normalizes and validates phone numbers for WhatsApp integration.
"""

import re
import phonenumbers
from typing import Optional, Tuple, Dict, Any
from phonenumbers.phonenumberutil import NumberParseException


class PhoneNormalizer:
    """
    Normalizes and validates phone numbers for WhatsApp integration.
    
    Handles international phone number formatting and validation
    for different regions and formats.
    """
    
    @staticmethod
    def normalize_phone(phone: str, country_code: str = 'US') -> Optional[str]:
        """
        Normalize a phone number to international format.
        
        Args:
            phone: Phone number to normalize
            country_code: Default country code (ISO 3166-1 alpha-2)
            
        Returns:
            Optional[str]: Normalized phone number in E.164 format, or None if invalid
        """
        if not phone:
            return None
        
        # Clean the phone number
        cleaned_phone = PhoneNormalizer._clean_phone_number(phone)
        
        if not cleaned_phone:
            return None
        
        try:
            # Parse the phone number
            parsed_number = phonenumbers.parse(cleaned_phone, country_code)
            
            # Check if it's a valid number
            if phonenumbers.is_valid_number(parsed_number):
                # Format to E.164
                return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            
        except NumberParseException:
            # Try to parse without country code
            try:
                parsed_number = phonenumbers.parse(cleaned_phone, None)
                if phonenumbers.is_valid_number(parsed_number):
                    return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            except NumberParseException:
                pass
        
        return None
    
    @staticmethod
    def _clean_phone_number(phone: str) -> str:
        """Clean phone number by removing non-digit characters."""
        if not phone:
            return ""
        
        # Remove all non-digit characters except leading +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Handle multiple + signs
        if cleaned.count('+') > 1:
            cleaned = cleaned.replace('+', '')  # Remove all + signs
        elif cleaned.startswith('+'):
            # Keep the + at the beginning
            pass
        else:
            # No + sign, ensure it's just digits
            cleaned = re.sub(r'\D', '', cleaned)
        
        return cleaned
    
    @staticmethod
    def validate_whatsapp_phone(phone: str, country_code: str = 'US') -> Tuple[bool, Optional[str]]:
        """
        Validate phone number for WhatsApp compatibility.
        
        Args:
            phone: Phone number to validate
            country_code: Default country code
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, normalized_number)
        """
        normalized = PhoneNormalizer.normalize_phone(phone, country_code)
        
        if not normalized:
            return False, None
        
        # Additional WhatsApp-specific validation
        # WhatsApp typically requires numbers to be:
        # - At least 9 digits (excluding country code)
        # - Not a landline (in most cases)
        
        try:
            parsed_number = phonenumbers.parse(normalized, None)
            
            # Check minimum length
            if parsed_number.national_number < 100000000:  # 9 digits minimum
                return False, None
            
            # Check if it's a mobile number (WhatsApp typically doesn't support landlines)
            if phonenumbers.number_type(parsed_number) not in [
                phonenumbers.PhoneNumberType.MOBILE,
                phonenumbers.PhoneNumberType.VOIP,
                phonenumbers.PhoneNumberType.UNKNOWN
            ]:
                return False, None
            
            return True, normalized
            
        except NumberParseException:
            return False, None
    
    @staticmethod
    def extract_phone_from_text(text: str) -> Optional[str]:
        """
        Extract phone number from text.
        
        Args:
            text: Text to search for phone numbers
            
        Returns:
            Optional[str]: First valid phone number found, or None
        """
        if not text:
            return None
        
        # Common phone number patterns
        patterns = [
            r'\+?\d{1,3}[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+?\d{11,15}',  # International format
            r'\d{10,15}',  # Just digits
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # Try to normalize each match
                normalized = PhoneNormalizer.normalize_phone(match)
                if normalized:
                    return normalized
        
        return None
    
    @staticmethod
    def format_phone_for_display(phone: str, format_type: str = 'national') -> Optional[str]:
        """
        Format phone number for display purposes.
        
        Args:
            phone: Phone number to format
            format_type: Format type ('national', 'international', 'e164')
            
        Returns:
            Optional[str]: Formatted phone number
        """
        if not phone:
            return None
        
        try:
            parsed_number = phonenumbers.parse(phone, None)
            
            if format_type == 'national':
                return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL)
            elif format_type == 'international':
                return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            elif format_type == 'e164':
                return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            else:
                return phone
                
        except NumberParseException:
            return phone
    
    @staticmethod
    def get_country_info(phone: str) -> Dict[str, Any]:
        """
        Get country information from phone number.
        
        Args:
            phone: Phone number to analyze
            
        Returns:
            Dict[str, Any]: Country information
        """
        if not phone:
            return {}
        
        try:
            parsed_number = phonenumbers.parse(phone, None)
            
            return {
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number,
                'region_code': phonenumbers.region_code_for_number(parsed_number),
                'country_name': phonenumbers.region_code_for_number(parsed_number),
                'is_valid': phonenumbers.is_valid_number(parsed_number),
                'is_possible': phonenumbers.is_possible_number(parsed_number),
                'number_type': phonenumbers.number_type(parsed_number).name,
                'formatted_national': PhoneNormalizer.format_phone_for_display(phone, 'national'),
                'formatted_international': PhoneNormalizer.format_phone_for_display(phone, 'international')
            }
            
        except NumberParseException:
            return {}
    
    @staticmethod
    def is_whatsapp_supported(phone: str) -> bool:
        """
        Check if phone number is supported by WhatsApp.
        
        Args:
            phone: Phone number to check
            
        Returns:
            bool: True if supported, False otherwise
        """
        if not phone:
            return False
        
        # Basic validation
        is_valid, normalized = PhoneNormalizer.validate_whatsapp_phone(phone)
        if not is_valid:
            return False
        
        # Check if the country supports WhatsApp
        try:
            parsed_number = phonenumbers.parse(normalized, None)
            region_code = phonenumbers.region_code_for_number(parsed_number)
            
            # List of countries that support WhatsApp (this is not exhaustive)
            whatsapp_supported_countries = [
                'US', 'CA', 'GB', 'DE', 'FR', 'IT', 'ES', 'AU', 'BR', 'IN', 'JP', 'KR',
                'MX', 'AR', 'CO', 'CL', 'PE', 'VE', 'EC', 'BO', 'PY', 'UY', 'GF', 'SR',
                'UY', 'PA', 'CR', 'NI', 'HN', 'SV', 'GT', 'BZ', 'JM', 'TT', 'BB', 'BS',
                'GD', 'KN', 'LC', 'VC', 'AG', 'DM', 'GY', 'SR', 'GF', 'MQ', 'RE', 'YT',
                'BL', 'MF', 'PM', 'WF', 'PF', 'NC', 'PF', 'AS', 'GU', 'MP', 'VI', 'PR',
                'DO', 'HT', 'CU', 'PR', 'VI', 'GU', 'MP', 'AS', 'UM', 'FM', 'MH', 'PW',
                'KI', 'NR', 'TV', 'TO', 'WS', 'FJ', 'VU', 'SB', 'CK', 'NU', 'PF', 'NC',
                'WF', 'PF', 'AS', 'GU', 'MP', 'VI', 'PR', 'DO', 'HT', 'CU', 'PR', 'VI',
                'GU', 'MP', 'AS', 'UM', 'FM', 'MH', 'PW', 'KI', 'NR', 'TV', 'TO', 'WS',
                'FJ', 'VU', 'SB', 'CK', 'NU', 'PF', 'NC', 'WF', 'PF'
            ]
            
            return region_code in whatsapp_supported_countries
            
        except NumberParseException:
            return False
    
    @staticmethod
    def batch_normalize_phones(phones: list, country_code: str = 'US') -> Dict[str, Any]:
        """
        Normalize a batch of phone numbers.
        
        Args:
            phones: List of phone numbers to normalize
            country_code: Default country code
            
        Returns:
            Dict[str, Any]: Batch normalization results
        """
        results = {
            'total': len(phones),
            'valid': 0,
            'invalid': 0,
            'normalized': [],
            'errors': []
        }
        
        for i, phone in enumerate(phones):
            try:
                normalized = PhoneNormalizer.normalize_phone(phone, country_code)
                is_valid_whatsapp = False
                
                if normalized:
                    is_valid_whatsapp, _ = PhoneNormalizer.validate_whatsapp_phone(phone, country_code)
                    results['valid'] += 1
                else:
                    results['invalid'] += 1
                
                results['normalized'].append({
                    'original': phone,
                    'normalized': normalized,
                    'is_valid_whatsapp': is_valid_whatsapp,
                    'index': i
                })
                
            except Exception as e:
                results['invalid'] += 1
                results['errors'].append({
                    'phone': phone,
                    'error': str(e),
                    'index': i
                })
        
        return results
    
    @staticmethod
    def detect_phone_format(phone: str) -> str:
        """
        Detect the format of a phone number.
        
        Args:
            phone: Phone number to analyze
            
        Returns:
            str: Detected format ('e164', 'international', 'national', 'unknown')
        """
        if not phone:
            return 'unknown'
        
        # Check for E.164 format (starts with + and digits only)
        if re.match(r'^\+\d+$', phone):
            return 'e164'
        
        # Check for international format (+XX XXX XXX XXXX)
        if re.match(r'^\+\d{1,3}\s?\d{3,}\s?\d{3,}\s?\d{3,}$', phone):
            return 'international'
        
        # Check for national format (XXX-XXX-XXXX)
        if re.match(r'^\d{3}[-.\s]?\d{3}[-.\s]?\d{4}$', phone):
            return 'national'
        
        # Check for just digits
        if re.match(r'^\d{10,15}$', phone):
            return 'digits'
        
        return 'unknown'
    
    @staticmethod
    def estimate_carrier(phone: str) -> Optional[str]:
        """
        Estimate carrier information from phone number.
        
        Args:
            phone: Phone number to analyze
            
        Returns:
            Optional[str]: Carrier name or None
        """
        if not phone:
            return None
        
        try:
            # This is a simplified carrier detection
            # In a real implementation, you might use a carrier lookup service
            parsed_number = phonenumbers.parse(phone, None)
            region_code = phonenumbers.region_code_for_number(parsed_number)
            
            # Basic carrier mapping (this is very simplified)
            carrier_map = {
                'US': ['AT&T', 'Verizon', 'T-Mobile', 'Sprint'],
                'GB': ['Vodafone', 'O2', 'EE', 'Three'],
                'DE': ['Telekom', 'Vodafone', 'O2'],
                'FR': ['Orange', 'SFR', 'Bouygues'],
                'IT': ['TIM', 'Vodafone', 'Wind', 'Tre'],
                'ES': ['Movistar', 'Vodafone', 'Orange'],
                'BR': ['Vivo', 'Claro', 'TIM', 'Oi'],
                'IN': ['Airtel', 'Jio', 'Vi', 'BSNL'],
                'CA': ['Rogers', 'Bell', 'Telus'],
                'AU': ['Telstra', 'Optus', 'Vodafone'],
                'MX': ['Telcel', 'Movistar', 'AT&T'],
                'AR': ['Claro', 'Personal', 'Movistar'],
                'CO': ['Movistar', 'Claro', 'Tigo'],
                'CL': ['Entel', 'Claro', 'Movistar'],
                'PE': ['Claro', 'Movistar', 'Bitel'],
                'VE': ['Movistar', 'Digitel', 'Movilnet'],
                'EC': ['Claro', 'Movistar', 'CNT'],
                'BO': ['Viva', 'Entel', 'Tigo'],
                'PY': ['Personal', 'Claro', 'Tigo'],
                'UY': ['Movistar', 'Claro', 'Antel'],
                'GF': ['Orange', 'SFR', 'Bouygues'],
                'SR': ['Telesur', 'Digicel', 'Uniqa'],
                'JM': ['Digicel', 'Flow'],
                'TT': ['Digicel', 'Flow'],
                'BB': ['Flow', 'Digicel'],
                'BS': ['BTC', 'Aliv', 'Flow'],
                'GD': ['Flow', 'Digicel'],
                'KN': ['Flow', 'Digicel'],
                'LC': ['Flow', 'Digicel'],
                'VC': ['Flow', 'Digicel'],
                'AG': ['Flow', 'Digicel'],
                'DM': ['Flow', 'Digicel'],
                'GY': ['Digicel', 'GT&T'],
                'MQ': ['Orange', 'SFR', 'Bouygues'],
                'RE': ['Orange', 'SFR', 'Bouygues'],
                'YT': ['Orange', 'SFR', 'Bouygues'],
                'BL': ['Orange', 'SFR', 'Bouygues'],
                'MF': ['Orange', 'SFR', 'Bouygues'],
                'PM': ['Orange', 'SFR', 'Bouygues'],
                'WF': ['Orange', 'SFR', 'Bouygues'],
                'PF': ['Orange', 'Vodafone', 'Manuia'],
                'NC': ['Optus', 'Vodafone', 'NC Numérique'],
                'AS': ['AT&T', 'Hawaiian Telcom'],
                'GU': ['Guam Cellular', 'Hawaiian Telcom'],
                'MP': ['MP Tel', 'Hawaiian Telcom'],
                'VI': ['AT&T', 'Claro'],
                'PR': ['Claro', 'AT&T', 'Open Mobile'],
                'DO': ['Claro', 'Altice', 'Viva'],
                'HT': ['Digicel', 'Natcom'],
                'CU': ['Cubacel', 'ETECSA'],
                'FM': ['FSMTC', 'Pacific Tele'],
                'MH': ['AT&T', 'Hawaiian Telcom'],
                'PW': ['Palau National', 'Pacific Tele'],
                'KI': ['TCI', 'Kiribati Telecom'],
                'NR': ['Nauru Telecom'],
                'TV': ['TVL', 'Digicel'],
                'TO': ['Digicel', 'Tonfon'],
                'WS': ['Digicel', 'Bluesky'],
                'FJ': ['Vodafone', 'Fiji TV'],
                'VU': ['Digicel', 'Vanuatu Telecom'],
                'SB': ['Solomon Telecom', 'Bmobile'],
                'CK': ['Vodafone', 'Cook Islands Telecom'],
                'NU': ['Niue Telecom'],
                'CK': ['Vodafone', 'Cook Islands Telecom'],
                'NU': ['Niue Telecom'],
                'PF': ['Orange', 'Vodafone', 'Manuia'],
                'NC': ['Optus', 'Vodafone', 'NC Numérique'],
                'WF': ['Orange', 'SFR', 'Bouygues'],
                'PF': ['Orange', 'Vodafone', 'Manuia'],
                'AS': ['AT&T', 'Hawaiian Telcom'],
                'GU': ['Guam Cellular', 'Hawaiian Telcom'],
                'MP': ['MP Tel', 'Hawaiian Telcom'],
                'VI': ['AT&T', 'Claro'],
                'PR': ['Claro', 'AT&T', 'Open Mobile'],
                'DO': ['Claro', 'Altice', 'Viva'],
                'HT': ['Digicel', 'Natcom'],
                'CU': ['Cubacel', 'ETECSA'],
                'FM': ['FSMTC', 'Pacific Tele'],
                'MH': ['AT&T', 'Hawaiian Telcom'],
                'PW': ['Palau National', 'Pacific Tele'],
                'KI': ['TCI', 'Kiribati Telecom'],
                'NR': ['Nauru Telecom'],
                'TV': ['TVL', 'Digicel'],
                'TO': ['Digicel', 'Tonfon'],
                'WS': ['Digicel', 'Bluesky'],
                'FJ': ['Vodafone', 'Fiji TV'],
                'VU': ['Digicel', 'Vanuatu Telecom'],
                'SB': ['Solomon Telecom', 'Bmobile'],
                'CK': ['Vodafone', 'Cook Islands Telecom'],
                'NU': ['Niue Telecom']
            }
            
            carriers = carrier_map.get(region_code, ['Unknown'])
            return carriers[0] if carriers else 'Unknown'
            
        except NumberParseException:
            return None
    
    @staticmethod
    def test_phone_number(phone: str, country_code: str = 'US') -> Dict[str, Any]:
        """
        Comprehensive phone number test.
        
        Args:
            phone: Phone number to test
            country_code: Default country code
            
        Returns:
            Dict[str, Any]: Test results
        """
        results = {
            'original': phone,
            'normalized': None,
            'is_valid': False,
            'is_valid_whatsapp': False,
            'format': 'unknown',
            'country_info': {},
            'carrier': None,
            'errors': []
        }
        
        try:
            # Normalize
            normalized = PhoneNormalizer.normalize_phone(phone, country_code)
            results['normalized'] = normalized
            
            if normalized:
                # Validate
                results['is_valid'] = True
                
                # WhatsApp validation
                results['is_valid_whatsapp'], _ = PhoneNormalizer.validate_whatsapp_phone(phone, country_code)
                
                # Format detection
                results['format'] = PhoneNormalizer.detect_phone_format(phone)
                
                # Country info
                results['country_info'] = PhoneNormalizer.get_country_info(phone)
                
                # Carrier estimation
                results['carrier'] = PhoneNormalizer.estimate_carrier(phone)
            else:
                results['errors'].append('Invalid phone number format')
                
        except Exception as e:
            results['errors'].append(str(e))
        
        return results