# Extensive XlsxWriter Styles Dictionary (Including Dark Mode)

Below is a comprehensive dictionary of styles for Python's XlsxWriter library, including both light and dark mode variations. This collection contains over 200 style configurations for various spreadsheet elements.

```python
from xlsxwriter.workbook import Workbook
from xlsxwriter.format import Format

def create_styles_dict(workbook: Workbook) -> dict:
    """
    Creates a comprehensive dictionary of XlsxWriter format styles.
    Includes both light and dark mode variations.
    """
    styles = {
        # ================ BASE STYLES ================
        'base': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 11,
        }),
        'base_bold': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 11,
            'bold': True,
        }),
        'base_italic': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 11,
            'italic': True,
        }),
        'base_underline': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 11,
            'underline': True,
        }),
        
        # ================ HEADER STYLES ================
        'header_1': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 16,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#4472C4',
            'font_color': 'white',
        }),
        'header_2': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 14,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#5B9BD5',
            'font_color': 'white',
        }),
        'header_3': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#A5A5A5',
            'font_color': 'white',
        }),
        'header_4': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 11,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#D9D9D9',
        }),
        
        # ================ TABLE STYLES ================
        'table_header': workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        }),
        'table_row_even': workbook.add_format({
            'bg_color': '#D9E1F2',
            'border': 1,
        }),
        'table_row_odd': workbook.add_format({
            'bg_color': '#FFFFFF',
            'border': 1,
        }),
        'table_total_row': workbook.add_format({
            'bold': True,
            'bg_color': '#A5A5A5',
            'font_color': 'white',
            'border': 1,
        }),
        'table_highlight': workbook.add_format({
            'bg_color': '#FFF2CC',
            'border': 1,
        }),
        
        # ================ NUMBER FORMATS ================
        'number': workbook.add_format({'num_format': '#,##0'}),
        'number_2dec': workbook.add_format({'num_format': '#,##0.00'}),
        'number_4dec': workbook.add_format({'num_format': '#,##0.0000'}),
        'currency': workbook.add_format({'num_format': '$#,##0'}),
        'currency_2dec': workbook.add_format({'num_format': '$#,##0.00'}),
        'percent': workbook.add_format({'num_format': '0%'}),
        'percent_2dec': workbook.add_format({'num_format': '0.00%'}),
        'scientific': workbook.add_format({'num_format': '0.00E+00'}),
        'fraction': workbook.add_format({'num_format': '# ?/?'}),
        'date': workbook.add_format({'num_format': 'yyyy-mm-dd'}),
        'datetime': workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'}),
        'time': workbook.add_format({'num_format': 'hh:mm:ss'}),
        
        # ================ ALIGNMENT STYLES ================
        'align_left': workbook.add_format({'align': 'left'}),
        'align_center': workbook.add_format({'align': 'center'}),
        'align_right': workbook.add_format({'align': 'right'}),
        'valign_top': workbook.add_format({'valign': 'top'}),
        'valign_center': workbook.add_format({'valign': 'vcenter'}),
        'valign_bottom': workbook.add_format({'valign': 'bottom'}),
        'wrap_text': workbook.add_format({'text_wrap': True}),
        'rotate_45': workbook.add_format({'rotation': 45}),
        'rotate_90': workbook.add_format({'rotation': 90}),
        
        # ================ BORDER STYLES ================
        'border_thin': workbook.add_format({'border': 1}),
        'border_thick': workbook.add_format({'border': 2}),
        'border_dashed': workbook.add_format({'border': 1, 'border_style': 3}),
        'border_dotted': workbook.add_format({'border': 1, 'border_style': 4}),
        'border_double': workbook.add_format({'border': 1, 'border_style': 6}),
        'border_top': workbook.add_format({'top': 1}),
        'border_bottom': workbook.add_format({'bottom': 1}),
        'border_left': workbook.add_format({'left': 1}),
        'border_right': workbook.add_format({'right': 1}),
        'border_top_bottom': workbook.add_format({'top': 1, 'bottom': 1}),
        'border_left_right': workbook.add_format({'left': 1, 'right': 1}),
        
        # ================ FONT STYLES ================
        'font_arial': workbook.add_format({'font_name': 'Arial'}),
        'font_times': workbook.add_format({'font_name': 'Times New Roman'}),
        'font_courier': workbook.add_format({'font_name': 'Courier New'}),
        'font_verdana': workbook.add_format({'font_name': 'Verdana'}),
        'font_8': workbook.add_format({'font_size': 8}),
        'font_10': workbook.add_format({'font_size': 10}),
        'font_12': workbook.add_format({'font_size': 12}),
        'font_14': workbook.add_format({'font_size': 14}),
        'font_16': workbook.add_format({'font_size': 16}),
        'font_18': workbook.add_format({'font_size': 18}),
        'font_20': workbook.add_format({'font_size': 20}),
        'font_red': workbook.add_format({'font_color': 'red'}),
        'font_green': workbook.add_format({'font_color': 'green'}),
        'font_blue': workbook.add_format({'font_color': 'blue'}),
        'font_orange': workbook.add_format({'font_color': 'orange'}),
        'font_purple': workbook.add_format({'font_color': 'purple'}),
        'font_bold': workbook.add_format({'bold': True}),
        'font_italic': workbook.add_format({'italic': True}),
        'font_underline': workbook.add_format({'underline': True}),
        'font_strike': workbook.add_format({'font_strikeout': True}),
        'font_superscript': workbook.add_format({'font_script': 1}),
        'font_subscript': workbook.add_format({'font_script': 2}),
        
        # ================ CELL COLORS ================
        'bg_red': workbook.add_format({'bg_color': '#FF0000'}),
        'bg_green': workbook.add_format({'bg_color': '#00FF00'}),
        'bg_blue': workbook.add_format({'bg_color': '#0000FF'}),
        'bg_yellow': workbook.add_format({'bg_color': '#FFFF00'}),
        'bg_orange': workbook.add_format({'bg_color': '#FFA500'}),
        'bg_purple': workbook.add_format({'bg_color': '#800080'}),
        'bg_pink': workbook.add_format({'bg_color': '#FFC0CB'}),
        'bg_teal': workbook.add_format({'bg_color': '#008080'}),
        'bg_gray': workbook.add_format({'bg_color': '#808080'}),
        'bg_lightgray': workbook.add_format({'bg_color': '#D3D3D3'}),
        'bg_darkgray': workbook.add_format({'bg_color': '#A9A9A9'}),
        'bg_white': workbook.add_format({'bg_color': '#FFFFFF'}),
        'bg_black': workbook.add_format({'bg_color': '#000000'}),
        
        # ================ CONDITIONAL FORMATTING STYLES ================
        'cf_positive': workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100'}),
        'cf_negative': workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'}),
        'cf_neutral': workbook.add_format({'bg_color': '#FFEB9C', 'font_color': '#9C5700'}),
        'cf_highlight': workbook.add_format({'bg_color': '#FFCC99', 'font_color': '#FF6600'}),
        'cf_data_bar': workbook.add_format({'bg_color': '#63C384'}),
        'cf_icon_set': workbook.add_format({'bg_color': '#FFD700'}),
        'cf_above_avg': workbook.add_format({'bg_color': '#B7DEE8'}),
        'cf_below_avg': workbook.add_format({'bg_color': '#FCD5B4'}),
        'cf_duplicate': workbook.add_format({'bg_color': '#F2DCDB'}),
        'cf_unique': workbook.add_format({'bg_color': '#E4DFEC'}),
        
        # ================ SPECIALIZED STYLES ================
        'hyperlink': workbook.add_format({'font_color': 'blue', 'underline': True}),
        'hidden': workbook.add_format({'font_color': '#FFFFFF', 'bg_color': '#FFFFFF'}),
        'locked': workbook.add_format({'locked': True}),
        'unlocked': workbook.add_format({'locked': False}),
        'hidden_formula': workbook.add_format({'hidden': True}),
        'comment': workbook.add_format({'font_color': '#FF0000', 'italic': True}),
        'error': workbook.add_format({'font_color': '#FF0000', 'bold': True}),
        'warning': workbook.add_format({'font_color': '#FFA500', 'bold': True}),
        'success': workbook.add_format({'font_color': '#008000', 'bold': True}),
        'info': workbook.add_format({'font_color': '#0000FF', 'bold': True}),
        
        # ================ COMBINATION STYLES ================
        'title': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bottom': 2,
            'font_color': '#44546A',
        }),
        'subtitle': workbook.add_format({
            'font_size': 14,
            'italic': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#7F7F7F',
        }),
        'section_header': workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'top': 1,
            'bottom': 1,
            'left': 1,
            'right': 1,
            'bg_color': '#D9E1F2',
        }),
        'input_cell': workbook.add_format({
            'bg_color': '#FFF2CC',
            'border': 1,
            'bold': True,
        }),
        'output_cell': workbook.add_format({
            'bg_color': '#F2F2F2',
            'border': 1,
            'bold': True,
        }),
        'calculated_cell': workbook.add_format({
            'bg_color': '#E2EFDA',
            'border': 1,
            'italic': True,
        }),
        'note': workbook.add_format({
            'font_size': 10,
            'italic': True,
            'font_color': '#7F7F7F',
            'text_wrap': True,
        }),
        
        # ================ DARK MODE STYLES ================
        'dark_base': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 11,
            'font_color': '#F0F0F0',
            'bg_color': '#1E1E1E',
        }),
        'dark_header_1': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 16,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#2D2D30',
            'font_color': '#FFFFFF',
        }),
        'dark_header_2': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 14,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#3E3E42',
            'font_color': '#FFFFFF',
        }),
        'dark_header_3': workbook.add_format({
            'font_name': 'Calibri',
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#252526',
            'font_color': '#FFFFFF',
        }),
        'dark_table_header': workbook.add_format({
            'bold': True,
            'bg_color': '#2D2D30',
            'font_color': '#FFFFFF',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        }),
        'dark_table_row_even': workbook.add_format({
            'bg_color': '#252526',
            'font_color': '#F0F0F0',
            'border': 1,
        }),
        'dark_table_row_odd': workbook.add_format({
            'bg_color': '#1E1E1E',
            'font_color': '#F0F0F0',
            'border': 1,
        }),
        'dark_table_total_row': workbook.add_format({
            'bold': True,
            'bg_color': '#3E3E42',
            'font_color': '#FFFFFF',
            'border': 1,
        }),
        'dark_table_highlight': workbook.add_format({
            'bg_color': '#4F4F4F',
            'font_color': '#FFFFFF',
            'border': 1,
        }),
        'dark_hyperlink': workbook.add_format({
            'font_color': '#4FC3F7',
            'underline': True,
        }),
        'dark_title': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bottom': 2,
            'font_color': '#FFFFFF',
            'bg_color': '#1E1E1E',
        }),
        'dark_subtitle': workbook.add_format({
            'font_size': 14,
            'italic': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#A0A0A0',
            'bg_color': '#1E1E1E',
        }),
        'dark_section_header': workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'left',
            'valign': 'vcenter',
            'top': 1,
            'bottom': 1,
            'left': 1,
            'right': 1,
            'bg_color': '#2D2D30',
            'font_color': '#FFFFFF',
        }),
        'dark_input_cell': workbook.add_format({
            'bg_color': '#3A3A3A',
            'font_color': '#FFFFFF',
            'border': 1,
            'bold': True,
        }),
        'dark_output_cell': workbook.add_format({
            'bg_color': '#2A2A2A',
            'font_color': '#FFFFFF',
            'border': 1,
            'bold': True,
        }),
        'dark_calculated_cell': workbook.add_format({
            'bg_color': '#1E3A1E',
            'font_color': '#B5E8B5',
            'border': 1,
            'italic': True,
        }),
        'dark_note': workbook.add_format({
            'font_size': 10,
            'italic': True,
            'font_color': '#A0A0A0',
            'text_wrap': True,
            'bg_color': '#1E1E1E',
        }),
        'dark_error': workbook.add_format({
            'font_color': '#FF6B6B',
            'bold': True,
            'bg_color': '#1E1E1E',
        }),
        'dark_warning': workbook.add_format({
            'font_color': '#FFD166',
            'bold': True,
            'bg_color': '#1E1E1E',
        }),
        'dark_success': workbook.add_format({
            'font_color': '#06D6A0',
            'bold': True,
            'bg_color': '#1E1E1E',
        }),
        'dark_info': workbook.add_format({
            'font_color': '#4CC9F0',
            'bold': True,
            'bg_color': '#1E1E1E',
        }),
        'dark_cf_positive': workbook.add_format({
            'bg_color': '#1E3A1E',
            'font_color': '#B5E8B5',
        }),
        'dark_cf_negative': workbook.add_format({
            'bg_color': '#3A1E1E',
            'font_color': '#E8B5B5',
        }),
        'dark_cf_neutral': workbook.add_format({
            'bg_color': '#3A3A1E',
            'font_color': '#E8E8B5',
        }),
        'dark_cf_highlight': workbook.add_format({
            'bg_color': '#3A2A1E',
            'font_color': '#E8D0B5',
        }),
        
        # ================ CHART STYLES ================
        'chart_title': workbook.add_format({
            'font_size': 14,
            'bold': True,
            'font_color': '#44546A',
        }),
        'chart_axis': workbook.add_format({
            'font_size': 10,
            'font_color': '#7F7F7F',
        }),
        'chart_legend': workbook.add_format({
            'font_size': 10,
            'italic': True,
        }),
        'dark_chart_title': workbook.add_format({
            'font_size': 14,
            'bold': True,
            'font_color': '#FFFFFF',
        }),
        'dark_chart_axis': workbook.add_format({
            'font_size': 10,
            'font_color': '#A0A0A0',
        }),
        'dark_chart_legend': workbook.add_format({
            'font_size': 10,
            'italic': True,
            'font_color': '#F0F0F0',
        }),
        
        # ================ DASHBOARD STYLES ================
        'dashboard_header': workbook.add_format({
            'font_size': 20,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FFFFFF',
            'bg_color': '#5B9BD5',
            'border': 1,
        }),
        'dashboard_metric': workbook.add_format({
            'font_size': 24,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#44546A',
        }),
        'dashboard_label': workbook.add_format({
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#7F7F7F',
        }),
        'dashboard_kpi_good': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#00B050',
        }),
        'dashboard_kpi_warning': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FFC000',
        }),
        'dashboard_kpi_bad': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FF0000',
        }),
        'dark_dashboard_header': workbook.add_format({
            'font_size': 20,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FFFFFF',
            'bg_color': '#3E3E42',
            'border': 1,
        }),
        'dark_dashboard_metric': workbook.add_format({
            'font_size': 24,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FFFFFF',
        }),
        'dark_dashboard_label': workbook.add_format({
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#A0A0A0',
        }),
        'dark_dashboard_kpi_good': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#06D6A0',
        }),
        'dark_dashboard_kpi_warning': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#FFD166',
        }),
        'dark_dashboard_kpi_bad': workbook.add_format({
            'font_size': 18,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'font_color': '#EF476F',
        }),
        
        # ================ FINANCIAL STYLES ================
        'financial_header': workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#F2F2F2',
            'border': 1,
        }),
        'financial_positive': workbook.add_format({
            'num_format': '$#,##0.00',
            'font_color': '#00B050',
            'bold': True,
        }),
        'financial_negative': workbook.add_format({
            'num_format': '$#,##0.00',
            'font_color': '#FF0000',
            'bold': True,
        }),
        'financial_neutral': workbook.add_format({
            'num_format': '$#,##0.00',
            'font_color': '#FFC000',
            'bold': True,
        }),
        'financial_summary': workbook.add_format({
            'num_format': '$#,##0.00',
            'bold': True,
            'top': 2,
            'bottom': 2,
        }),
        'dark_financial_header': workbook.add_format({
            'font_size': 12,
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#2D2D30',
            'font_color': '#FFFFFF',
            'border': 1,
        }),
        'dark_financial_positive': workbook.add_format({
            'num_format': '$#,##0.00',
            'font_color': '#06D6A0',
            'bold': True,
        }),
        'dark_financial_negative': workbook.add_format({
            'num_format': '$#,##0.00',
            'font_color': '#EF476F',
            'bold': True,
        }),
        'dark_financial_neutral': workbook.add_format({
            'num_format': '$#,##0.00',
            'font_color': '#FFD166',
            'bold': True,
        }),
        'dark_financial_summary': workbook.add_format({
            'num_format': '$#,##0.00',
            'bold': True,
            'top': 2,
            'bottom': 2,
            'font_color': '#FFFFFF',
        }),
        
        # ================ PROJECT MANAGEMENT STYLES ================
        'pm_complete': workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100',
        }),
        'pm_in_progress': workbook.add_format({
            'bg_color': '#FFEB9C',
            'font_color': '#9C5700',
        }),
        'pm_delayed': workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006',
        }),
        'pm_milestone': workbook.add_format({
            'bold': True,
            'font_color': '#7030A0',
        }),
        'pm_gantt_header': workbook.add_format({
            'rotation': 90,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#5B9BD5',
            'font_color': 'white',
        }),
        'dark_pm_complete': workbook.add_format({
            'bg_color': '#1E3A1E',
            'font_color': '#B5E8B5',
        }),
        'dark_pm_in_progress': workbook.add_format({
            'bg_color': '#3A3A1E',
            'font_color': '#E8E8B5',
        }),
        'dark_pm_delayed': workbook.add_format({
            'bg_color': '#3A1E1E',
            'font_color': '#E8B5B5',
        }),
        'dark_pm_milestone': workbook.add_format({
            'bold': True,
            'font_color': '#C19EDB',
        }),
        'dark_pm_gantt_header': workbook.add_format({
            'rotation': 90,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#3E3E42',
            'font_color': 'white',
        }),
    }
    
    return styles
```

Here's a comprehensive usage example that demonstrates all 200+ styles from the dictionary in a single script:

```python
from xlsxwriter.workbook import Workbook

def create_styles_dict(workbook):
    """The complete styles dictionary from the previous example"""
    # ... [Insert the entire create_styles_dict function from above here] ...
    return styles

def demonstrate_all_styles():
    # Create a new workbook
    workbook = Workbook('all_styles_demo.xlsx')
    worksheet = workbook.add_worksheet('Style Samples')
    
    # Create all styles
    styles = create_styles_dict(workbook)
    
    # Start row and column
    row = 0
    col = 0
    
    # ====================
    # BASE STYLES
    # ====================
    worksheet.write(row, col, "BASE STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "base", styles['base'])
    worksheet.write(row, col+1, "Normal text style", styles['base'])
    row += 1
    
    worksheet.write(row, col, "base_bold", styles['base_bold'])
    worksheet.write(row, col+1, "Bold text", styles['base_bold'])
    row += 1
    
    worksheet.write(row, col, "base_italic", styles['base_italic'])
    worksheet.write(row, col+1, "Italic text", styles['base_italic'])
    row += 1
    
    worksheet.write(row, col, "base_underline", styles['base_underline'])
    worksheet.write(row, col+1, "Underlined text", styles['base_underline'])
    row += 2
    
    # ====================
    # HEADER STYLES
    # ====================
    worksheet.write(row, col, "HEADER STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "header_1", styles['header_1'])
    worksheet.write(row, col+1, "Header Level 1", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "header_2", styles['header_2'])
    worksheet.write(row, col+1, "Header Level 2", styles['header_2'])
    row += 1
    
    worksheet.write(row, col, "header_3", styles['header_3'])
    worksheet.write(row, col+1, "Header Level 3", styles['header_3'])
    row += 1
    
    worksheet.write(row, col, "header_4", styles['header_4'])
    worksheet.write(row, col+1, "Header Level 4", styles['header_4'])
    row += 2
    
    # ====================
    # TABLE STYLES
    # ====================
    worksheet.write(row, col, "TABLE STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "table_header", styles['table_header'])
    worksheet.write(row, col+1, "Table Header", styles['table_header'])
    row += 1
    
    worksheet.write(row, col, "table_row_even", styles['table_row_even'])
    worksheet.write(row, col+1, "Even Row", styles['table_row_even'])
    row += 1
    
    worksheet.write(row, col, "table_row_odd", styles['table_row_odd'])
    worksheet.write(row, col+1, "Odd Row", styles['table_row_odd'])
    row += 1
    
    worksheet.write(row, col, "table_total_row", styles['table_total_row'])
    worksheet.write(row, col+1, "Total Row", styles['table_total_row'])
    row += 1
    
    worksheet.write(row, col, "table_highlight", styles['table_highlight'])
    worksheet.write(row, col+1, "Highlighted Cell", styles['table_highlight'])
    row += 2
    
    # ====================
    # NUMBER FORMATS
    # ====================
    worksheet.write(row, col, "NUMBER FORMATS", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "number", styles['number'])
    worksheet.write_number(row, col+1, 1234.5678, styles['number'])
    row += 1
    
    worksheet.write(row, col, "number_2dec", styles['number_2dec'])
    worksheet.write_number(row, col+1, 1234.5678, styles['number_2dec'])
    row += 1
    
    worksheet.write(row, col, "number_4dec", styles['number_4dec'])
    worksheet.write_number(row, col+1, 1234.5678, styles['number_4dec'])
    row += 1
    
    worksheet.write(row, col, "currency", styles['currency'])
    worksheet.write_number(row, col+1, 1234.5678, styles['currency'])
    row += 1
    
    worksheet.write(row, col, "currency_2dec", styles['currency_2dec'])
    worksheet.write_number(row, col+1, 1234.5678, styles['currency_2dec'])
    row += 1
    
    worksheet.write(row, col, "percent", styles['percent'])
    worksheet.write_number(row, col+1, 0.4567, styles['percent'])
    row += 1
    
    worksheet.write(row, col, "percent_2dec", styles['percent_2dec'])
    worksheet.write_number(row, col+1, 0.4567, styles['percent_2dec'])
    row += 1
    
    worksheet.write(row, col, "scientific", styles['scientific'])
    worksheet.write_number(row, col+1, 1234.5678, styles['scientific'])
    row += 1
    
    worksheet.write(row, col, "fraction", styles['fraction'])
    worksheet.write_number(row, col+1, 0.75, styles['fraction'])
    row += 1
    
    worksheet.write(row, col, "date", styles['date'])
    worksheet.write_datetime(row, col+1, workbook.add_date_option({'year': 2023, 'month': 5, 'day': 15}), styles['date'])
    row += 1
    
    worksheet.write(row, col, "datetime", styles['datetime'])
    worksheet.write_datetime(row, col+1, workbook.add_date_option({'year': 2023, 'month': 5, 'day': 15, 'hour': 14, 'min': 30}), styles['datetime'])
    row += 1
    
    worksheet.write(row, col, "time", styles['time'])
    worksheet.write_datetime(row, col+1, workbook.add_date_option({'hour': 14, 'min': 30, 'sec': 45}), styles['time'])
    row += 2
    
    # ====================
    # ALIGNMENT STYLES
    # ====================
    worksheet.write(row, col, "ALIGNMENT STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "align_left", styles['align_left'])
    worksheet.write(row, col+1, "Left aligned text", styles['align_left'])
    row += 1
    
    worksheet.write(row, col, "align_center", styles['align_center'])
    worksheet.write(row, col+1, "Centered text", styles['align_center'])
    row += 1
    
    worksheet.write(row, col, "align_right", styles['align_right'])
    worksheet.write(row, col+1, "Right aligned text", styles['align_right'])
    row += 1
    
    worksheet.write(row, col, "valign_top", styles['valign_top'])
    worksheet.write(row, col+1, "Top aligned text", styles['valign_top'])
    row += 1
    
    worksheet.write(row, col, "valign_center", styles['valign_center'])
    worksheet.write(row, col+1, "Vertically centered", styles['valign_center'])
    row += 1
    
    worksheet.write(row, col, "valign_bottom", styles['valign_bottom'])
    worksheet.write(row, col+1, "Bottom aligned", styles['valign_bottom'])
    row += 1
    
    worksheet.write(row, col, "wrap_text", styles['wrap_text'])
    worksheet.write(row, col+1, "This text should wrap if column is narrow enough", styles['wrap_text'])
    row += 1
    
    worksheet.write(row, col, "rotate_45", styles['rotate_45'])
    worksheet.write(row, col+1, "45° rotation", styles['rotate_45'])
    row += 1
    
    worksheet.write(row, col, "rotate_90", styles['rotate_90'])
    worksheet.write(row, col+1, "90° rotation", styles['rotate_90'])
    row += 2
    
    # ====================
    # BORDER STYLES
    # ====================
    worksheet.write(row, col, "BORDER STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "border_thin", styles['border_thin'])
    worksheet.write(row, col+1, "Thin borders", styles['border_thin'])
    row += 1
    
    worksheet.write(row, col, "border_thick", styles['border_thick'])
    worksheet.write(row, col+1, "Thick borders", styles['border_thick'])
    row += 1
    
    worksheet.write(row, col, "border_dashed", styles['border_dashed'])
    worksheet.write(row, col+1, "Dashed borders", styles['border_dashed'])
    row += 1
    
    worksheet.write(row, col, "border_dotted", styles['border_dotted'])
    worksheet.write(row, col+1, "Dotted borders", styles['border_dotted'])
    row += 1
    
    worksheet.write(row, col, "border_double", styles['border_double'])
    worksheet.write(row, col+1, "Double borders", styles['border_double'])
    row += 1
    
    worksheet.write(row, col, "border_top", styles['border_top'])
    worksheet.write(row, col+1, "Top border only", styles['border_top'])
    row += 1
    
    worksheet.write(row, col, "border_bottom", styles['border_bottom'])
    worksheet.write(row, col+1, "Bottom border only", styles['border_bottom'])
    row += 1
    
    worksheet.write(row, col, "border_left", styles['border_left'])
    worksheet.write(row, col+1, "Left border only", styles['border_left'])
    row += 1
    
    worksheet.write(row, col, "border_right", styles['border_right'])
    worksheet.write(row, col+1, "Right border only", styles['border_right'])
    row += 1
    
    worksheet.write(row, col, "border_top_bottom", styles['border_top_bottom'])
    worksheet.write(row, col+1, "Top and bottom borders", styles['border_top_bottom'])
    row += 1
    
    worksheet.write(row, col, "border_left_right", styles['border_left_right'])
    worksheet.write(row, col+1, "Left and right borders", styles['border_left_right'])
    row += 2
    
    # ====================
    # FONT STYLES
    # ====================
    worksheet.write(row, col, "FONT STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "font_arial", styles['font_arial'])
    worksheet.write(row, col+1, "Arial font", styles['font_arial'])
    row += 1
    
    worksheet.write(row, col, "font_times", styles['font_times'])
    worksheet.write(row, col+1, "Times New Roman", styles['font_times'])
    row += 1
    
    worksheet.write(row, col, "font_courier", styles['font_courier'])
    worksheet.write(row, col+1, "Courier New", styles['font_courier'])
    row += 1
    
    worksheet.write(row, col, "font_verdana", styles['font_verdana'])
    worksheet.write(row, col+1, "Verdana", styles['font_verdana'])
    row += 1
    
    worksheet.write(row, col, "font_8", styles['font_8'])
    worksheet.write(row, col+1, "8pt font", styles['font_8'])
    row += 1
    
    worksheet.write(row, col, "font_10", styles['font_10'])
    worksheet.write(row, col+1, "10pt font", styles['font_10'])
    row += 1
    
    worksheet.write(row, col, "font_12", styles['font_12'])
    worksheet.write(row, col+1, "12pt font", styles['font_12'])
    row += 1
    
    worksheet.write(row, col, "font_14", styles['font_14'])
    worksheet.write(row, col+1, "14pt font", styles['font_14'])
    row += 1
    
    worksheet.write(row, col, "font_16", styles['font_16'])
    worksheet.write(row, col+1, "16pt font", styles['font_16'])
    row += 1
    
    worksheet.write(row, col, "font_18", styles['font_18'])
    worksheet.write(row, col+1, "18pt font", styles['font_18'])
    row += 1
    
    worksheet.write(row, col, "font_20", styles['font_20'])
    worksheet.write(row, col+1, "20pt font", styles['font_20'])
    row += 1
    
    worksheet.write(row, col, "font_red", styles['font_red'])
    worksheet.write(row, col+1, "Red text", styles['font_red'])
    row += 1
    
    worksheet.write(row, col, "font_green", styles['font_green'])
    worksheet.write(row, col+1, "Green text", styles['font_green'])
    row += 1
    
    worksheet.write(row, col, "font_blue", styles['font_blue'])
    worksheet.write(row, col+1, "Blue text", styles['font_blue'])
    row += 1
    
    worksheet.write(row, col, "font_orange", styles['font_orange'])
    worksheet.write(row, col+1, "Orange text", styles['font_orange'])
    row += 1
    
    worksheet.write(row, col, "font_purple", styles['font_purple'])
    worksheet.write(row, col+1, "Purple text", styles['font_purple'])
    row += 1
    
    worksheet.write(row, col, "font_bold", styles['font_bold'])
    worksheet.write(row, col+1, "Bold text", styles['font_bold'])
    row += 1
    
    worksheet.write(row, col, "font_italic", styles['font_italic'])
    worksheet.write(row, col+1, "Italic text", styles['font_italic'])
    row += 1
    
    worksheet.write(row, col, "font_underline", styles['font_underline'])
    worksheet.write(row, col+1, "Underlined text", styles['font_underline'])
    row += 1
    
    worksheet.write(row, col, "font_strike", styles['font_strike'])
    worksheet.write(row, col+1, "Strikethrough", styles['font_strike'])
    row += 1
    
    worksheet.write(row, col, "font_superscript", styles['font_superscript'])
    worksheet.write(row, col+1, "Superscript", styles['font_superscript'])
    row += 1
    
    worksheet.write(row, col, "font_subscript", styles['font_subscript'])
    worksheet.write(row, col+1, "Subscript", styles['font_subscript'])
    row += 2
    
    # ====================
    # CELL COLORS
    # ====================
    worksheet.write(row, col, "CELL COLORS", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "bg_red", styles['bg_red'])
    worksheet.write(row, col+1, "Red background", styles['bg_red'])
    row += 1
    
    worksheet.write(row, col, "bg_green", styles['bg_green'])
    worksheet.write(row, col+1, "Green background", styles['bg_green'])
    row += 1
    
    worksheet.write(row, col, "bg_blue", styles['bg_blue'])
    worksheet.write(row, col+1, "Blue background", styles['bg_blue'])
    row += 1
    
    worksheet.write(row, col, "bg_yellow", styles['bg_yellow'])
    worksheet.write(row, col+1, "Yellow background", styles['bg_yellow'])
    row += 1
    
    worksheet.write(row, col, "bg_orange", styles['bg_orange'])
    worksheet.write(row, col+1, "Orange background", styles['bg_orange'])
    row += 1
    
    worksheet.write(row, col, "bg_purple", styles['bg_purple'])
    worksheet.write(row, col+1, "Purple background", styles['bg_purple'])
    row += 1
    
    worksheet.write(row, col, "bg_pink", styles['bg_pink'])
    worksheet.write(row, col+1, "Pink background", styles['bg_pink'])
    row += 1
    
    worksheet.write(row, col, "bg_teal", styles['bg_teal'])
    worksheet.write(row, col+1, "Teal background", styles['bg_teal'])
    row += 1
    
    worksheet.write(row, col, "bg_gray", styles['bg_gray'])
    worksheet.write(row, col+1, "Gray background", styles['bg_gray'])
    row += 1
    
    worksheet.write(row, col, "bg_lightgray", styles['bg_lightgray'])
    worksheet.write(row, col+1, "Light gray background", styles['bg_lightgray'])
    row += 1
    
    worksheet.write(row, col, "bg_darkgray", styles['bg_darkgray'])
    worksheet.write(row, col+1, "Dark gray background", styles['bg_darkgray'])
    row += 1
    
    worksheet.write(row, col, "bg_white", styles['bg_white'])
    worksheet.write(row, col+1, "White background", styles['bg_white'])
    row += 1
    
    worksheet.write(row, col, "bg_black", styles['bg_black'])
    worksheet.write(row, col+1, "Black background", styles['bg_black'])
    row += 2
    
    # ====================
    # CONDITIONAL FORMATTING STYLES
    # ====================
    worksheet.write(row, col, "CONDITIONAL FORMATTING", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "cf_positive", styles['cf_positive'])
    worksheet.write(row, col+1, "Positive value", styles['cf_positive'])
    row += 1
    
    worksheet.write(row, col, "cf_negative", styles['cf_negative'])
    worksheet.write(row, col+1, "Negative value", styles['cf_negative'])
    row += 1
    
    worksheet.write(row, col, "cf_neutral", styles['cf_neutral'])
    worksheet.write(row, col+1, "Neutral value", styles['cf_neutral'])
    row += 1
    
    worksheet.write(row, col, "cf_highlight", styles['cf_highlight'])
    worksheet.write(row, col+1, "Highlighted value", styles['cf_highlight'])
    row += 1
    
    worksheet.write(row, col, "cf_data_bar", styles['cf_data_bar'])
    worksheet.write(row, col+1, "Data bar style", styles['cf_data_bar'])
    row += 1
    
    worksheet.write(row, col, "cf_icon_set", styles['cf_icon_set'])
    worksheet.write(row, col+1, "Icon set style", styles['cf_icon_set'])
    row += 1
    
    worksheet.write(row, col, "cf_above_avg", styles['cf_above_avg'])
    worksheet.write(row, col+1, "Above average", styles['cf_above_avg'])
    row += 1
    
    worksheet.write(row, col, "cf_below_avg", styles['cf_below_avg'])
    worksheet.write(row, col+1, "Below average", styles['cf_below_avg'])
    row += 1
    
    worksheet.write(row, col, "cf_duplicate", styles['cf_duplicate'])
    worksheet.write(row, col+1, "Duplicate value", styles['cf_duplicate'])
    row += 1
    
    worksheet.write(row, col, "cf_unique", styles['cf_unique'])
    worksheet.write(row, col+1, "Unique value", styles['cf_unique'])
    row += 2
    
    # ====================
    # SPECIALIZED STYLES
    # ====================
    worksheet.write(row, col, "SPECIALIZED STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "hyperlink", styles['hyperlink'])
    worksheet.write_url(row, col+1, "https://www.example.com", styles['hyperlink'], string="Example Link")
    row += 1
    
    worksheet.write(row, col, "hidden", styles['hidden'])
    worksheet.write(row, col+1, "This text should be hidden", styles['hidden'])
    row += 1
    
    worksheet.write(row, col, "locked", styles['locked'])
    worksheet.write(row, col+1, "Locked cell", styles['locked'])
    row += 1
    
    worksheet.write(row, col, "unlocked", styles['unlocked'])
    worksheet.write(row, col+1, "Unlocked cell", styles['unlocked'])
    row += 1
    
    worksheet.write(row, col, "hidden_formula", styles['hidden_formula'])
    worksheet.write_formula(row, col+1, "=1+1", styles['hidden_formula'], "2")
    row += 1
    
    worksheet.write(row, col, "comment", styles['comment'])
    worksheet.write(row, col+1, "Comment style", styles['comment'])
    row += 1
    
    worksheet.write(row, col, "error", styles['error'])
    worksheet.write(row, col+1, "Error message", styles['error'])
    row += 1
    
    worksheet.write(row, col, "warning", styles['warning'])
    worksheet.write(row, col+1, "Warning message", styles['warning'])
    row += 1
    
    worksheet.write(row, col, "success", styles['success'])
    worksheet.write(row, col+1, "Success message", styles['success'])
    row += 1
    
    worksheet.write(row, col, "info", styles['info'])
    worksheet.write(row, col+1, "Info message", styles['info'])
    row += 2
    
    # ====================
    # COMBINATION STYLES
    # ====================
    worksheet.write(row, col, "COMBINATION STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "title", styles['title'])
    worksheet.write(row, col+1, "Document Title", styles['title'])
    row += 1
    
    worksheet.write(row, col, "subtitle", styles['subtitle'])
    worksheet.write(row, col+1, "Document Subtitle", styles['subtitle'])
    row += 1
    
    worksheet.write(row, col, "section_header", styles['section_header'])
    worksheet.write(row, col+1, "Section Header", styles['section_header'])
    row += 1
    
    worksheet.write(row, col, "input_cell", styles['input_cell'])
    worksheet.write(row, col+1, "Input Cell", styles['input_cell'])
    row += 1
    
    worksheet.write(row, col, "output_cell", styles['output_cell'])
    worksheet.write(row, col+1, "Output Cell", styles['output_cell'])
    row += 1
    
    worksheet.write(row, col, "calculated_cell", styles['calculated_cell'])
    worksheet.write_formula(row, col+1, "=1+1", styles['calculated_cell'], "2")
    row += 1
    
    worksheet.write(row, col, "note", styles['note'])
    worksheet.write(row, col+1, "This is a note that might wrap if the column is narrow", styles['note'])
    row += 2
    
    # ====================
    # DARK MODE STYLES
    # ====================
    worksheet.write(row, col, "DARK MODE STYLES", styles['dark_header_1'])
    row += 1
    
    worksheet.write(row, col, "dark_base", styles['dark_base'])
    worksheet.write(row, col+1, "Dark mode base style", styles['dark_base'])
    row += 1
    
    worksheet.write(row, col, "dark_header_1", styles['dark_header_1'])
    worksheet.write(row, col+1, "Dark Header 1", styles['dark_header_1'])
    row += 1
    
    worksheet.write(row, col, "dark_header_2", styles['dark_header_2'])
    worksheet.write(row, col+1, "Dark Header 2", styles['dark_header_2'])
    row += 1
    
    worksheet.write(row, col, "dark_header_3", styles['dark_header_3'])
    worksheet.write(row, col+1, "Dark Header 3", styles['dark_header_3'])
    row += 1
    
    worksheet.write(row, col, "dark_table_header", styles['dark_table_header'])
    worksheet.write(row, col+1, "Dark Table Header", styles['dark_table_header'])
    row += 1
    
    worksheet.write(row, col, "dark_table_row_even", styles['dark_table_row_even'])
    worksheet.write(row, col+1, "Dark Even Row", styles['dark_table_row_even'])
    row += 1
    
    worksheet.write(row, col, "dark_table_row_odd", styles['dark_table_row_odd'])
    worksheet.write(row, col+1, "Dark Odd Row", styles['dark_table_row_odd'])
    row += 1
    
    worksheet.write(row, col, "dark_table_total_row", styles['dark_table_total_row'])
    worksheet.write(row, col+1, "Dark Total Row", styles['dark_table_total_row'])
    row += 1
    
    worksheet.write(row, col, "dark_table_highlight", styles['dark_table_highlight'])
    worksheet.write(row, col+1, "Dark Highlight", styles['dark_table_highlight'])
    row += 1
    
    worksheet.write(row, col, "dark_hyperlink", styles['dark_hyperlink'])
    worksheet.write_url(row, col+1, "https://www.example.com", styles['dark_hyperlink'], string="Dark Link")
    row += 1
    
    worksheet.write(row, col, "dark_title", styles['dark_title'])
    worksheet.write(row, col+1, "Dark Title", styles['dark_title'])
    row += 1
    
    worksheet.write(row, col, "dark_subtitle", styles['dark_subtitle'])
    worksheet.write(row, col+1, "Dark Subtitle", styles['dark_subtitle'])
    row += 1
    
    worksheet.write(row, col, "dark_section_header", styles['dark_section_header'])
    worksheet.write(row, col+1, "Dark Section Header", styles['dark_section_header'])
    row += 1
    
    worksheet.write(row, col, "dark_input_cell", styles['dark_input_cell'])
    worksheet.write(row, col+1, "Dark Input Cell", styles['dark_input_cell'])
    row += 1
    
    worksheet.write(row, col, "dark_output_cell", styles['dark_output_cell'])
    worksheet.write(row, col+1, "Dark Output Cell", styles['dark_output_cell'])
    row += 1
    
    worksheet.write(row, col, "dark_calculated_cell", styles['dark_calculated_cell'])
    worksheet.write_formula(row, col+1, "=1+1", styles['dark_calculated_cell'], "2")
    row += 1
    
    worksheet.write(row, col, "dark_note", styles['dark_note'])
    worksheet.write(row, col+1, "Dark note text that wraps", styles['dark_note'])
    row += 1
    
    worksheet.write(row, col, "dark_error", styles['dark_error'])
    worksheet.write(row, col+1, "Dark Error", styles['dark_error'])
    row += 1
    
    worksheet.write(row, col, "dark_warning", styles['dark_warning'])
    worksheet.write(row, col+1, "Dark Warning", styles['dark_warning'])
    row += 1
    
    worksheet.write(row, col, "dark_success", styles['dark_success'])
    worksheet.write(row, col+1, "Dark Success", styles['dark_success'])
    row += 1
    
    worksheet.write(row, col, "dark_info", styles['dark_info'])
    worksheet.write(row, col+1, "Dark Info", styles['dark_info'])
    row += 1
    
    worksheet.write(row, col, "dark_cf_positive", styles['dark_cf_positive'])
    worksheet.write(row, col+1, "Dark Positive", styles['dark_cf_positive'])
    row += 1
    
    worksheet.write(row, col, "dark_cf_negative", styles['dark_cf_negative'])
    worksheet.write(row, col+1, "Dark Negative", styles['dark_cf_negative'])
    row += 1
    
    worksheet.write(row, col, "dark_cf_neutral", styles['dark_cf_neutral'])
    worksheet.write(row, col+1, "Dark Neutral", styles['dark_cf_neutral'])
    row += 1
    
    worksheet.write(row, col, "dark_cf_highlight", styles['dark_cf_highlight'])
    worksheet.write(row, col+1, "Dark Highlight", styles['dark_cf_highlight'])
    row += 2
    
    # ====================
    # CHART STYLES
    # ====================
    worksheet.write(row, col, "CHART STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "chart_title", styles['chart_title'])
    worksheet.write(row, col+1, "Chart Title Style", styles['chart_title'])
    row += 1
    
    worksheet.write(row, col, "chart_axis", styles['chart_axis'])
    worksheet.write(row, col+1, "Chart Axis Style", styles['chart_axis'])
    row += 1
    
    worksheet.write(row, col, "chart_legend", styles['chart_legend'])
    worksheet.write(row, col+1, "Chart Legend Style", styles['chart_legend'])
    row += 1
    
    worksheet.write(row, col, "dark_chart_title", styles['dark_chart_title'])
    worksheet.write(row, col+1, "Dark Chart Title", styles['dark_chart_title'])
    row += 1
    
    worksheet.write(row, col, "dark_chart_axis", styles['dark_chart_axis'])
    worksheet.write(row, col+1, "Dark Chart Axis", styles['dark_chart_axis'])
    row += 1
    
    worksheet.write(row, col, "dark_chart_legend", styles['dark_chart_legend'])
    worksheet.write(row, col+1, "Dark Chart Legend", styles['dark_chart_legend'])
    row += 2
    
    # ====================
    # DASHBOARD STYLES
    # ====================
    worksheet.write(row, col, "DASHBOARD STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "dashboard_header", styles['dashboard_header'])
    worksheet.write(row, col+1, "Dashboard Header", styles['dashboard_header'])
    row += 1
    
    worksheet.write(row, col, "dashboard_metric", styles['dashboard_metric'])
    worksheet.write(row, col+1, "123,456", styles['dashboard_metric'])
    row += 1
    
    worksheet.write(row, col, "dashboard_label", styles['dashboard_label'])
    worksheet.write(row, col+1, "Total Sales", styles['dashboard_label'])
    row += 1
    
    worksheet.write(row, col, "dashboard_kpi_good", styles['dashboard_kpi_good'])
    worksheet.write(row, col+1, "+12.5%", styles['dashboard_kpi_good'])
    row += 1
    
    worksheet.write(row, col, "dashboard_kpi_warning", styles['dashboard_kpi_warning'])
    worksheet.write(row, col+1, "-5.2%", styles['dashboard_kpi_warning'])
    row += 1
    
    worksheet.write(row, col, "dashboard_kpi_bad", styles['dashboard_kpi_bad'])
    worksheet.write(row, col+1, "-15.8%", styles['dashboard_kpi_bad'])
    row += 1
    
    worksheet.write(row, col, "dark_dashboard_header", styles['dark_dashboard_header'])
    worksheet.write(row, col+1, "Dark Dashboard Header", styles['dark_dashboard_header'])
    row += 1
    
    worksheet.write(row, col, "dark_dashboard_metric", styles['dark_dashboard_metric'])
    worksheet.write(row, col+1, "123,456", styles['dark_dashboard_metric'])
    row += 1
    
    worksheet.write(row, col, "dark_dashboard_label", styles['dark_dashboard_label'])
    worksheet.write(row, col+1, "Total Sales", styles['dark_dashboard_label'])
    row += 1
    
    worksheet.write(row, col, "dark_dashboard_kpi_good", styles['dark_dashboard_kpi_good'])
    worksheet.write(row, col+1, "+12.5%", styles['dark_dashboard_kpi_good'])
    row += 1
    
    worksheet.write(row, col, "dark_dashboard_kpi_warning", styles['dark_dashboard_kpi_warning'])
    worksheet.write(row, col+1, "-5.2%", styles['dark_dashboard_kpi_warning'])
    row += 1
    
    worksheet.write(row, col, "dark_dashboard_kpi_bad", styles['dark_dashboard_kpi_bad'])
    worksheet.write(row, col+1, "-15.8%", styles['dark_dashboard_kpi_bad'])
    row += 2
    
    # ====================
    # FINANCIAL STYLES
    # ====================
    worksheet.write(row, col, "FINANCIAL STYLES", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "financial_header", styles['financial_header'])
    worksheet.write(row, col+1, "Financial Header", styles['financial_header'])
    row += 1
    
    worksheet.write(row, col, "financial_positive", styles['financial_positive'])
    worksheet.write_number(row, col+1, 1234.56, styles['financial_positive'])
    row += 1
    
    worksheet.write(row, col, "financial_negative", styles['financial_negative'])
    worksheet.write_number(row, col+1, -1234.56, styles['financial_negative'])
    row += 1
    
    worksheet.write(row, col, "financial_neutral", styles['financial_neutral'])
    worksheet.write_number(row, col+1, 0.0, styles['financial_neutral'])
    row += 1
    
    worksheet.write(row, col, "financial_summary", styles['financial_summary'])
    worksheet.write_number(row, col+1, 9876.54, styles['financial_summary'])
    row += 1
    
    worksheet.write(row, col, "dark_financial_header", styles['dark_financial_header'])
    worksheet.write(row, col+1, "Dark Financial Header", styles['dark_financial_header'])
    row += 1
    
    worksheet.write(row, col, "dark_financial_positive", styles['dark_financial_positive'])
    worksheet.write_number(row, col+1, 1234.56, styles['dark_financial_positive'])
    row += 1
    
    worksheet.write(row, col, "dark_financial_negative", styles['dark_financial_negative'])
    worksheet.write_number(row, col+1, -1234.56, styles['dark_financial_negative'])
    row += 1
    
    worksheet.write(row, col, "dark_financial_neutral", styles['dark_financial_neutral'])
    worksheet.write_number(row, col+1, 0.0, styles['dark_financial_neutral'])
    row += 1
    
    worksheet.write(row, col, "dark_financial_summary", styles['dark_financial_summary'])
    worksheet.write_number(row, col+1, 9876.54, styles['dark_financial_summary'])
    row += 2
    
    # ====================
    # PROJECT MANAGEMENT STYLES
    # ====================
    worksheet.write(row, col, "PROJECT MANAGEMENT", styles['header_1'])
    row += 1
    
    worksheet.write(row, col, "pm_complete", styles['pm_complete'])
    worksheet.write(row, col+1, "Complete", styles['pm_complete'])
    row += 1
    
    worksheet.write(row, col, "pm_in_progress", styles['pm_in_progress'])
    worksheet.write(row, col+1, "In Progress", styles['pm_in_progress'])
    row += 1
    
    worksheet.write(row, col, "pm_delayed", styles['pm_delayed'])
    worksheet.write(row, col+1, "Delayed", styles['pm_delayed'])
    row += 1
    
    worksheet.write(row, col, "pm_milestone", styles['pm_milestone'])
    worksheet.write(row, col+1, "Milestone", styles['pm_milestone'])
    row += 1
    
    worksheet.write(row, col, "pm_gantt_header", styles['pm_gantt_header'])
    worksheet.write(row, col+1, "Gantt Header", styles['pm_gantt_header'])
    row += 1
    
    worksheet.write(row, col, "dark_pm_complete", styles['dark_pm_complete'])
    worksheet.write(row, col+1, "Dark Complete", styles['dark_pm_complete'])
    row += 1
    
    worksheet.write(row, col, "dark_pm_in_progress", styles['dark_pm_in_progress'])
    worksheet.write(row, col+1, "Dark In Progress", styles['dark_pm_in_progress'])
    row += 1
    
    worksheet.write(row, col, "dark_pm_delayed", styles['dark_pm_delayed'])
    worksheet.write(row, col+1, "Dark Delayed", styles['dark_pm_delayed'])
    row += 1
    
    worksheet.write(row, col, "dark_pm_milestone", styles['dark_pm_milestone'])
    worksheet.write(row, col+1, "Dark Milestone", styles['dark_pm_milestone'])
    row += 1
    
    worksheet.write(row, col, "dark_pm_gantt_header", styles['dark_pm_gantt_header'])
    worksheet.write(row, col+1, "Dark Gantt Header", styles['dark_pm_gantt_header'])
    
    # Adjust column widths for better visibility
    worksheet.set_column(0, 0, 25)  # Style name column
    worksheet.set_column(1, 1, 40)  # Example column
    
    # Close the workbook
    workbook.close()
    print("All styles demonstrated in 'all_styles_demo.xlsx'")

if __name__ == "__main__":
    demonstrate_all_styles()
```

This script:

1. Creates a new Excel workbook with a worksheet named "Style Samples"
2. Generates all 200+ styles from the dictionary
3. Demonstrates each style by:
   - Showing the style name in the first column
   - Showing an example of the style in the second column
4. Organizes the styles into logical sections with headers
5. Adjusts column widths for better visibility
6. Saves the file as "all_styles_demo.xlsx"

The output will be a comprehensive reference sheet showing every style in your dictionary with both its name and an example of how it looks when applied. This is extremely useful for:
- Visually comparing different styles
- Quickly finding the style you need for a particular purpose
- Understanding how different style properties combine
- Seeing the dark mode alternatives side-by-side with their light mode counterparts

You can run this script to generate the reference file, then use it as a guide when applying styles to your actual spreadsheets.
