"""
Core module for Shaheenviz - Main entry point for EDA report generation.

This module manages EDA mode selection and report generation, choosing between
YData Profiling and Sweetviz based on dataset characteristics.
"""

import pandas as pd
import numpy as np
from typing import Optional, Union, Dict, Any
import warnings
from tqdm import tqdm

# Fix matplotlib backend to prevent threading issues
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from .profiling_wrapper import ProfileWrapper
from .sweetviz_wrapper import SweetvizWrapper
from .utils import detect_target, save_reports


class ShaheenvizReport:
    """
    Main report class that wraps either YData Profiling or Sweetviz reports.
    """
    
    def __init__(self, backend_report, backend_type: str, metadata: Dict[str, Any]):
        """
        Initialize the unified report.
        
        Args:
            backend_report: The underlying report object (ProfileReport or SweetvizReport)
            backend_type: Either 'ydata' or 'sweetviz'
            metadata: Additional metadata about the report generation
        """
        self.backend_report = backend_report
        self.backend_type = backend_type
        self.metadata = metadata
    
    def save_html(self, filepath: str, **kwargs) -> None:
        """Save report as HTML file with custom Shaheenviz branding."""
        if self.backend_type == 'ydata':
            self.backend_report.to_file(filepath, **kwargs)
            # Post-process the HTML file to customize branding
            self._customize_html_file(filepath)
        elif self.backend_type == 'sweetviz':
            # Sweetviz uses show_html for saving files
            layout = kwargs.pop('layout', 'widescreen')
            scale = kwargs.pop('scale', 1.0)
            self.backend_report.show_html(filepath, layout=layout, scale=scale, **kwargs)
            # Post-process the HTML file to customize branding
            self._customize_html_file(filepath)
    
    def save_json(self, filepath: str) -> None:
        """Save report as JSON file (YData Profiling only)."""
        if self.backend_type == 'ydata':
            self.backend_report.to_file(filepath)
        else:
            warnings.warn("JSON export is only supported for YData Profiling backend")
    
    def show_notebook(self, **kwargs):
        """Display report in Jupyter notebook."""
        if self.backend_type == 'ydata':
            return self.backend_report.to_notebook_iframe(**kwargs)
        elif self.backend_type == 'sweetviz':
            return self.backend_report.show_notebook(**kwargs)
    
    def get_rejected_variables(self) -> list:
        """Get list of rejected variables (YData Profiling only)."""
        if self.backend_type == 'ydata':
            return self.backend_report.get_rejected_variables()
        else:
            warnings.warn("Rejected variables info is only available for YData Profiling backend")
            return []
    
    def _customize_html_file(self, filepath: str) -> None:
        """
        Post-process HTML file to replace YData branding with Shaheenviz branding.
        
        Args:
            filepath: Path to the HTML file to customize
        """
        try:
            print(f"🔧 Starting HTML customization for: {filepath}")
            
            # Read the HTML file
            with open(filepath, 'r', encoding='utf-8') as file:
                html_content = file.read()
            
            print(f"📄 Original HTML size: {len(html_content)} characters")
            
            # Apply branding customizations
            customized_content = self._apply_branding_replacements(html_content)
            
            print(f"📄 Customized HTML size: {len(customized_content)} characters")
            
            # Write the customized content back to the file
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(customized_content)
            
            print(f"✅ HTML customization completed for: {filepath}")
                
        except Exception as e:
            print(f"❌ Failed to customize HTML branding: {str(e)}")
            warnings.warn(f"Failed to customize HTML branding: {str(e)}")
    
    def _apply_branding_replacements(self, html_content: str) -> str:
        """
        Apply comprehensive branding replacements to HTML content.
        
        Args:
            html_content: Original HTML content
            
        Returns:
            HTML content with Shaheenviz branding
        """
        # Define replacement mappings
        replacements = {
            # Primary branding replacements (YData Profiling)
            'ydata-profiling': 'shaheenviz',
            'YData Profiling': 'Shaheenviz',
            'ydata_profiling': 'shaheenviz',
            'YData': 'Shaheenviz',
            'ydata': 'shaheenviz',
            
            # Sweetviz branding replacements
            'sweetviz': 'shaheenviz',
            'Sweetviz': 'Shaheenviz',
            'SweetViz': 'Shaheenviz',
            'SweetVIZ': 'Shaheenviz',
            'SWEETVIZ': 'SHAHEENVIZ',
            
            # Exact Sweetviz logo and version replacements
            'SweetViz\n                2.3.1': 'Shaheenviz\n                v1.0.0',
            'SweetViz 2.3.1': 'Shaheenviz v1.0.0',
            '2.3.1': 'v1.0.0',
            
            # Sweetviz specific links and references
            'https://github.com/fbdesignpro/sweetviz': 'https://github.com/hamza-0987/shaheenviz',
            'https://github.com/fbdesignpro/shaheenviz': 'https://github.com/hamza-0987/shaheenviz',
            'github.com/fbdesignpro/sweetviz': 'github.com/hamza-0987/shaheenviz',
            'github.com/fbdesignpro/shaheenviz': 'github.com/hamza-0987/shaheenviz',
            'fbdesignpro/sweetviz': 'hamza-0987/shaheenviz',
            'fbdesignpro/shaheenviz': 'hamza-0987/shaheenviz',
            'https://www.fbdesignpro.com': 'https://github.com/hamza-0987/shaheenviz',
            'fbdesignpro.com': 'github.com/hamza-0987/shaheenviz',
            'Francois Bertrand': 'Hamza',
            'Jean-Francois Hains': 'Shaheenviz Team',
            'Created & maintained by Francois Bertrand': 'Created & maintained by Hamza',
            'Created & maintained by': 'Created & maintained by',
            'Graphic design by Jean-Francois Hains': 'Developed by Shaheenviz Team',
            'Graphic design by': 'Developed by',
            'Get updates, docs & report issues here': 'Get updates, docs & report issues here',
            
            # Sweetviz titles and headers
            '<title>Sweetviz': '<title>Shaheenviz',
            'Sweetviz Report': 'Shaheenviz Report',
            'Generated by Sweetviz': 'Generated by Shaheenviz',
            'Powered by Sweetviz': 'Powered by Shaheenviz',
            
            # Meta tag replacements
            'content="ydata-profiling"': 'content="shaheenviz"',
            'content="YData Profiling"': 'content="Shaheenviz EDA Report"',
            'content="sweetviz"': 'content="shaheenviz"',
            'content="Sweetviz"': 'content="Shaheenviz EDA Report"',
            'name="ydata-profiling"': 'name="shaheenviz"',
            'name="sweetviz"': 'name="shaheenviz"',
            
            # Generator and author replacements
            'generator" content="ydata-profiling': 'generator" content="shaheenviz',
            'generator" content="sweetviz': 'generator" content="shaheenviz',
            'author" content="YData': 'author" content="Shaheenviz',
            'author" content="Sweetviz': 'author" content="Shaheenviz',
            
            # Link and reference replacements (YData)
            'https://github.com/ydataai/ydata-profiling': 'https://github.com/hamza-0987/shaheenviz',
            'github.com/ydataai/ydata-profiling': 'github.com/hamza-0987/shaheenviz',
            
            # Copyright and footer replacements
            '© YData': '© Shaheenviz',
            'YData Inc.': 'Shaheenviz',
            'ydata.ai': 'shaheenviz.dev',
            
            # Title and heading replacements
            '<title>YData': '<title>Shaheenviz',
            '<h1>YData': '<h1>Shaheenviz',
            '<h2>YData': '<h2>Shaheenviz',
            '<h1>Sweetviz': '<h1>Shaheenviz',
            '<h2>Sweetviz': '<h2>Shaheenviz',
            
            # CSS class and ID replacements (be careful not to break functionality)
            'ydata-': 'shaheenviz-',
            'sweetviz-': 'shaheenviz-',
            
            # JavaScript variable replacements
            'var ydata': 'var shaheenviz',
            'var sweetviz': 'var shaheenviz',
            'window.ydata': 'window.shaheenviz',
            'window.sweetviz': 'window.shaheenviz',
            
            # Description and metadata replacements
            'profiling report generated using ydata-profiling': 'profiling report generated using shaheenviz',
            'report generated using sweetviz': 'report generated using shaheenviz',
            'Generated by ydata-profiling': 'Generated by Shaheenviz',
            'Generated by sweetviz': 'Generated by Shaheenviz',
            'Powered by ydata-profiling': 'Powered by Shaheenviz',
            'Powered by sweetviz': 'Powered by Shaheenviz',
            
            # Version and package name replacements
            'ydata-profiling v': 'shaheenviz v',
            'sweetviz v': 'shaheenviz v',
            'package: ydata-profiling': 'package: shaheenviz',
            'package: sweetviz': 'package: shaheenviz',
        }
        
        # Apply all replacements
        customized_content = html_content
        for old_text, new_text in replacements.items():
            customized_content = customized_content.replace(old_text, new_text)
        
        # Add Tailwind CSS and Shadcn styles along with logo linking
        head_insertion = '''
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/shadcn@0.x.x/dist/shadcn.min.css" rel="stylesheet">  <!-- Replace with actual version -->
    <style>
        /* Shaheenviz Custom Dark Theme */
        body { 
            background: linear-gradient(135deg, #1f2937 0%, #111827 100%) !important;
            color: #f9fafb !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }
        
        .shaheenviz-header {
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            padding: 2rem 0;
            box-shadow: 0 4px 20px rgba(239, 68, 68, 0.3);
        }
        
        .shaheenviz-container { 
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        .shaheenviz-logo {
            display: flex;
            align-items: center;
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .shaheenviz-logo:hover {
            color: #fca5a5;
            transform: translateY(-2px);
        }
        
        .shaheenviz-logo img {
            width: 40px;
            height: 40px;
            margin-right: 12px;
            border-radius: 8px;
        }
        
        /* Override existing report styles */
        .navbar, nav {
            background: #374151 !important;
            border-bottom: 2px solid #ef4444 !important;
        }
        
        .navbar-brand, .nav-link {
            color: #f9fafb !important;
        }
        
        .nav-link:hover {
            color: #ef4444 !important;
        }
        
        .content, .section-items {
            background: #1f2937 !important;
            color: #f9fafb !important;
        }
        
        .table {
            background: #374151 !important;
            color: #f9fafb !important;
        }
        
        .table th {
            background: #ef4444 !important;
            color: white !important;
            border-color: #dc2626 !important;
        }
        
        .table td {
            border-color: #4b5563 !important;
        }
        
        .section-header h1 {
            color: #ef4444 !important;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 1.5rem !important;
        }
        
        .item-header {
            color: #ef4444 !important;
            font-weight: 600 !important;
        }
        
        .badge {
            background: #ef4444 !important;
            color: white !important;
        }
        
        .alert-info {
            background: #1e40af !important;
            border-color: #3b82f6 !important;
        }
        
        footer {
            background: #111827 !important;
            color: #9ca3af !important;
            text-align: center !important;
            padding: 2rem 0 !important;
            margin-top: 3rem !important;
            border-top: 2px solid #ef4444 !important;
        }
        
        /* Hide original Sweetviz branding */
        .sv-logo, .sweetviz-logo { display: none !important; }
        .sv-header { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important; }
    </style>
    '''
        header_content = '''
    <div class="shaheenviz-header">
        <div class="shaheenviz-container">
            <a href="https://github.com/hamza-0987/shaheenviz" class="shaheenviz-logo">
                <img src="logo.png" alt="Shaheenviz Logo"> Shaheenviz
            </a>
        </div>
    </div>
    '''
        customized_content = customized_content.replace('<head>', '<head>' + head_insertion)
        customized_content = customized_content.replace('<body>', '<body>' + header_content)
        
        return customized_content


def _choose_backend(df: pd.DataFrame, target: Optional[str] = None, 
                   mode: str = 'auto') -> str:
    """
    Choose the appropriate backend based on dataset characteristics.
    
    Args:
        df: Input DataFrame
        target: Target column name
        mode: 'auto', 'ydata', or 'sweetviz'
    
    Returns:
        Backend name: 'ydata' or 'sweetviz'
    """
    if mode in ['ydata', 'sweetviz']:
        return mode
    
    # Auto mode logic
    n_rows, n_cols = df.shape
    
    # Use Sweetviz for smaller datasets (better visualizations, interactive features)
    if n_rows < 5000 and n_cols < 30:
        print(f"Dataset size ({n_rows} rows, {n_cols} cols) - choosing Sweetviz for better visualizations")
        return 'sweetviz'
    
    # Use YData Profiling for larger datasets (better performance, more analysis)
    print(f"Dataset size ({n_rows} rows, {n_cols} cols) - choosing YData Profiling for better performance")
    return 'ydata'


def generate_report(df: pd.DataFrame, 
                   df2: Optional[pd.DataFrame] = None,
                   target: Optional[str] = None,
                   title: str = "Shaheenviz EDA Report",
                   mode: str = 'auto',
                   minimal: bool = False,
                   **kwargs) -> ShaheenvizReport:
    """
    Generate a comprehensive EDA report using the best available backend.
    
    Args:
        df: Primary DataFrame to analyze
        df2: Optional comparison DataFrame (e.g., validation set)
        target: Name of target column for supervised learning analysis
        title: Report title
        mode: Backend selection mode ('auto', 'ydata', 'sweetviz')
        minimal: Generate minimal report for faster processing
        **kwargs: Additional arguments passed to backend
    
    Returns:
        ShaheenvizReport object with unified interface
    """
    
    # Validate inputs
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame")
    
    if df.empty:
        raise ValueError("DataFrame cannot be empty")
    
    # Auto-detect target if not provided
    if target is None:
        target = detect_target(df)
        if target:
            print(f"Auto-detected target column: {target}")
    
    # Choose backend
    backend = _choose_backend(df, target, mode)
    print(f"Using {backend.upper()} backend for analysis...")
    
    # Generate metadata
    metadata = {
        'backend': backend,
        'dataset_shape': df.shape,
        'target_column': target,
        'comparison_dataset': df2 is not None,
        'minimal': minimal,
        'title': title
    }
    
    # Generate report based on chosen backend
    with tqdm(desc=f"Generating {backend.upper()} report", unit="step") as pbar:
        
        try:
            if backend == 'ydata':
                wrapper = ProfileWrapper()
                pbar.set_description("Initializing YData Profiling...")
                pbar.update(1)
                
                pbar.set_description("Generating YData profile...")
                report = wrapper.generate_profile(
                    df=df, 
                    target=target, 
                    title=title,
                    minimal=minimal,
                    **kwargs
                )
                pbar.set_description("YData profile complete")
                pbar.update(1)
                
            elif backend == 'sweetviz':
                wrapper = SweetvizWrapper()
                pbar.set_description("Initializing Sweetviz...")
                pbar.update(1)
                
                pbar.set_description("Generating Sweetviz report...")
                report = wrapper.generate_report(
                    df=df,
                    df2=df2,
                    target=target,
                    title=title,
                    **kwargs
                )
                pbar.set_description("Sweetviz report complete")
                pbar.update(1)
        
        except Exception as e:
            pbar.set_description(f"Error generating {backend.upper()} report")
            print(f"\n⚠️  Error with {backend.upper()} backend: {str(e)}")
            
            # Try fallback to the other backend
            fallback_backend = 'ydata' if backend == 'sweetviz' else 'sweetviz'
            print(f"🔄 Attempting fallback to {fallback_backend.upper()} backend...")
            
            try:
                if fallback_backend == 'ydata':
                    wrapper = ProfileWrapper()
                    report = wrapper.generate_profile(
                        df=df, 
                        target=target, 
                        title=title,
                        minimal=minimal,
                        **kwargs
                    )
                    backend = 'ydata'  # Update backend variable
                    metadata['backend'] = 'ydata'
                    metadata['fallback_used'] = True
                    print("✅ Fallback to YData Profiling successful")
                else:
                    wrapper = SweetvizWrapper()
                    report = wrapper.generate_report(
                        df=df,
                        df2=df2,
                        target=target,
                        title=title,
                        **kwargs
                    )
                    backend = 'sweetviz'  # Update backend variable
                    metadata['backend'] = 'sweetviz'
                    metadata['fallback_used'] = True
                    print("✅ Fallback to Sweetviz successful")
            
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Both backends failed. Original error ({backend}): {str(e)}. "
                    f"Fallback error ({fallback_backend}): {str(fallback_error)}"
                )
    
    return ShaheenvizReport(report, backend, metadata)


def compare_datasets(train_df: pd.DataFrame, 
                    test_df: pd.DataFrame,
                    target: Optional[str] = None,
                    title: str = "Dataset Comparison Report") -> ShaheenvizReport:
    """
    Generate a comparison report between training and test datasets.
    
    Args:
        train_df: Training DataFrame
        test_df: Test DataFrame  
        target: Target column name
        title: Report title
    
    Returns:
        ShaheenvizReport with comparison analysis
    """
    return generate_report(
        df=train_df,
        df2=test_df, 
        target=target,
        title=title,
        mode='sweetviz'  # Sweetviz is better for comparisons
    )


def quick_profile(df: pd.DataFrame, target: Optional[str] = None) -> ShaheenvizReport:
    """
    Generate a quick minimal profile for fast overview.
    
    Args:
        df: DataFrame to analyze
        target: Target column name
    
    Returns:
        Minimal ShaheenvizReport
    """
    return generate_report(
        df=df,
        target=target,
        title="Quick Profile",
        minimal=True,
        mode='ydata'  # YData Profiling has better minimal mode
    )
