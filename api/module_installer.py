"""
Module Installer
"""
from typing import Dict

class ModuleInstaller:
    def __init__(self):
        self.available_modules = {"python-3.11": {"name": "Python 3.11", "type": "language"}}
        self.installed_modules = ["python-3.11"]
    
    def list_available_modules(self, search: str = "") -> Dict:
        return {"success": True, "modules": [{"id": k, **v} for k, v in self.available_modules.items()]}
    
    def install_module(self, module_id: str) -> Dict:
        return {"success": True, "message": f"Module {module_id} installed"}
    
    def uninstall_module(self, module_id: str) -> Dict:
        return {"success": True, "message": f"Module {module_id} uninstalled"}
    
    def list_installed_modules(self) -> Dict:
        return {"success": True, "modules": self.installed_modules}
