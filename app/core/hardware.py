"""
Paksa AI Assistant - Hardware Identification

Provides hardware-based identification for license binding.
Copyright © 2025 Paksa IT Solutions (www.paksa.com.pk)
"""
import platform
import hashlib
import uuid
import subprocess
import re
import os
import sys
import socket
import psutil
from typing import Dict, Any, Optional

def get_mac_address() -> str:
    """Get the MAC address of the primary network interface"""
    try:
        # Get the MAC address of the default gateway interface
        if sys.platform == 'win32':
            # Windows
            result = subprocess.check_output(['getmac']).decode('utf-8')
            mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', result)
            if mac:
                return mac.group(0).replace('-', ':')
        else:
            # Linux/Mac
            result = subprocess.check_output(['ifconfig']).decode('utf-8')
            mac = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', result)
            if mac:
                return mac.group(0)
    except Exception:
        pass
    
    # Fallback to a random UUID if MAC address can't be determined
    return ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                    for elements in range(5, -1, -1)])

def get_cpu_id() -> str:
    """Get a unique identifier for the CPU"""
    try:
        if sys.platform == 'win32':
            # Windows
            result = subprocess.check_output(
                'wmic cpu get ProcessorId', 
                shell=True
            ).decode('utf-8')
            cpu_id = result.split('\n')[1].strip()
            return cpu_id
        else:
            # Linux/Mac
            result = subprocess.check_output(
                ['cat', '/proc/cpuinfo']
            ).decode('utf-8')
            for line in result.split('\n'):
                if 'serial' in line.lower():
                    return line.split(':')[1].strip()
    except Exception:
        pass
    
    # Fallback to a hash of the CPU info
    cpu_info = str(platform.processor()) + str(os.cpu_count())
    return hashlib.sha256(cpu_info.encode()).hexdigest()

def get_disk_serial() -> str:
    """Get the serial number of the primary disk"""
    try:
        if sys.platform == 'win32':
            # Windows
            result = subprocess.check_output(
                'wmic diskdrive get serialnumber', 
                shell=True
            ).decode('utf-8')
            serial = result.split('\n')[1].strip()
            return serial if serial else str(uuid.uuid4())
        else:
            # Linux/Mac
            result = subprocess.check_output(
                ['lsblk', '-d', '-o', 'SERIAL', '-n']
            ).decode('utf-8')
            return result.strip() or str(uuid.uuid4())
    except Exception:
        return str(uuid.uuid4())

def get_system_info() -> Dict[str, Any]:
    """Get system information for hardware fingerprinting"""
    return {
        'platform': platform.platform(),
        'system': platform.system(),
        'node': platform.node(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'cpu_count': os.cpu_count(),
        'total_ram': psutil.virtual_memory().total,
        'mac_address': get_mac_address(),
        'cpu_id': get_cpu_id(),
        'disk_serial': get_disk_serial(),
        'hostname': socket.gethostname(),
        'fqdn': socket.getfqdn(),
    }

def get_hardware_id(use_system_info: bool = True) -> str:
    """
    Generate a unique hardware identifier for the current machine
    
    Args:
        use_system_info: If True, includes detailed system info in the hash
        
    Returns:
        A string representing the hardware ID
    """
    if use_system_info:
        # Create a hash of the system information
        system_info = get_system_info()
        info_str = json.dumps(system_info, sort_keys=True)
        return hashlib.sha256(info_str.encode()).hexdigest()
    else:
        # Simple hardware ID based on MAC address and disk serial
        return hashlib.sha256(
            f"{get_mac_address()}:{get_disk_serial()}".encode()
        ).hexdigest()

def validate_hardware_id(hardware_id: str) -> bool:
    """
    Validate if a hardware ID matches the current system
    
    Args:
        hardware_id: The hardware ID to validate
        
    Returns:
        bool: True if the hardware ID is valid for this system
    """
    if not hardware_id:
        return False
    
    # Generate the current hardware ID with the same method
    current_id = get_hardware_id()
    
    # Compare the hardware IDs
    return current_id == hardware_id

# Example usage
if __name__ == "__main__":
    print("Hardware ID:", get_hardware_id())
    print("\nSystem Information:")
    import pprint
    pprint.pprint(get_system_info())
