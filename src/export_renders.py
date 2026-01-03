#!/usr/bin/env python3
"""
Export renders from FreeCAD files.
Usage: freecadcmd export_renders.py <input.FCStd> <output_dir>
"""

import sys
import os

# Check if we're running in FreeCAD
try:
    import FreeCAD as App
    import FreeCADGui as Gui
except ImportError:
    print("ERROR: This script must be run with freecadcmd or FreeCAD")
    sys.exit(1)

def export_renders(fcstd_path, output_dir):
    """Export multiple views from an FCStd file as PNG images"""
    
    if not os.path.exists(fcstd_path):
        print(f"ERROR: File not found: {fcstd_path}")
        return False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Import Qt for headless rendering
    from PySide import QtGui
    import platform
    
    # Initialize headless GUI (only on Linux)
    if platform.system() == 'Linux':
        try:
            QtGui.QApplication()
        except RuntimeError:
            pass
        
        Gui.showMainWindow()
        Gui.getMainWindow().destroy()
        App.ParamGet('User parameter:BaseApp/Preferences/Document').SetBool('SaveThumbnail', False)
    
    # Open the document
    print(f"Opening {fcstd_path}...")
    doc = App.openDocument(fcstd_path)
    
    # Create GUI document and view
    print("Creating 3D view...")
    Gui.setupWithoutGUI()
    Gui.activateWorkbench("PartWorkbench")
    
    # Get or create a view
    view = Gui.activeView()
    if not view:
        # Create a new 3D view
        Gui.getDocument(doc.Name)
        view = Gui.ActiveDocument.ActiveView
    
    if not view:
        print("ERROR: Could not create view")
        App.closeDocument(doc.Name)
        return False
    
    print(f"View created: {view}")
    
    # Get base name for output files
    base_name = os.path.splitext(os.path.basename(fcstd_path))[0]
    
    # Make all objects visible
    print("Setting objects visible...")
    for obj in doc.Objects:
        if hasattr(obj, 'ViewObject') and obj.ViewObject:
            try:
                if 'Origin' not in obj.Name:
                    obj.ViewObject.Visibility = True
            except:
                pass
    
    # Define views to export
    views = [
        ('Isometric', 'viewIsometric'),
        ('Front', 'viewFront'),
        ('Top', 'viewTop'),
        ('Right', 'viewRight'),
    ]
    
    # Disable animation for faster rendering
    try:
        view.setAnimationEnabled(False)
    except:
        pass
    
    # Export each view
    for view_name, view_method in views:
        print(f"Exporting {view_name} view...")
        
        # Set the view
        getattr(view, view_method)()
        view.fitAll()
        
        # Export as PNG
        output_path = os.path.join(output_dir, f"{base_name}_{view_name}.png")
        view.saveImage(output_path, 1920, 1080, 'White')
        
        print(f"  Saved: {output_path}")
    
    # Close document
    App.closeDocument(doc.Name)
    
    print(f"Exported {len(views)} views from {fcstd_path}")
    return True

if __name__ == "__main__":
    # Get arguments from environment variables (passed by Makefile)
    fcstd_path = os.environ.get('FCSTD_FILE')
    output_dir = os.environ.get('OUTPUT_DIR')
    
    if not fcstd_path or not output_dir:
        print("ERROR: FCSTD_FILE and OUTPUT_DIR environment variables must be set")
        print(f"FCSTD_FILE={fcstd_path}")
        print(f"OUTPUT_DIR={output_dir}")
        sys.exit(1)
    
    print(f"Input file: {fcstd_path}")
    print(f"Output dir: {output_dir}")
    
    success = export_renders(fcstd_path, output_dir)
    
    # Exit cleanly
    import os as _os
    _os._exit(0 if success else 1)
