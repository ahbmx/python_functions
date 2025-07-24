Here's a **complete draw.io XML template** for your SMC/TLC environment with virtual fabrics, including host ports, storage arrays, and detailed interconnections:

---

### **SAN Diagram XML Template**
```xml
<mxfile>
  <diagram name="SAN_Topology" id="SAN_Topology">
    <!-- ==================== LAYERS ==================== -->
    <mxLayer name="Physical" visible="1"/>
    <mxLayer name="Virtual_Fabrics" visible="1"/>
    <mxLayer name="Zoning" visible="0"/>
    
    <!-- ==================== SMC SITE ==================== -->
    <mxCell id="smc_site" value="SMC Site" style="swimlane;whiteSpace=wrap;html=1;fillColor=#E1F5FE;strokeColor=#0288D1;" parent="1" vertex="1">
      <mxGeometry x="100" y="100" width="1000" height="600"/>
    </mxCell>

    <!-- ~~~~~~~~~~~~ VIRTUAL FABRIC A ~~~~~~~~~~~~ -->
    <mxCell id="vf_a" value="Virtual Fabric A" style="swimlane;whiteSpace=wrap;html=1;fillColor=#FFF8E1;strokeColor=#FFA000;dashed=1;" parent="smc_site" vertex="1">
      <mxGeometry x="50" y="50" width="900" height="500"/>
    </mxCell>

    <!-- Core A Switch -->
    <mxCell id="smc_core_a" value="&lt;b&gt;SMC-Core-A&lt;/b&gt;&lt;br&gt;(Domain 1)" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;verticalAlign=top;aspect=fixed;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMTAwIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI0RBRThGQyIgc3Ryb2tlPSIjNkM4RUJGIi8+PHRleHQgeD0iMTAwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBhbGlnbm1lbnQtYmFzZWxpbmU9Im1pZGRsZSI+Q29yZS1BPC90ZXh0Pjwvc3ZnPg==;" parent="vf_a" vertex="1">
      <mxGeometry x="400" y="50" width="150" height="75"/>
    </mxCell>

    <!-- Edge A1 Switch -->
    <mxCell id="smc_edge_a1" value="&lt;b&gt;SMC-Edge-A1&lt;/b&gt;&lt;br&gt;(Domain 2)" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;verticalAlign=top;aspect=fixed;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNTAgNzUiPjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iNzUiIGZpbGw9IiNEQUU4RkMiIHN0cm9rZT0iIzZDQkVGRiIvPjx0ZXh0IHg9Ijc1IiB5PSIzOCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjEyIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBhbGlnbm1lbnQtYmFzZWxpbmU9Im1pZGRsZSI+RWRnZS1BMjwvdGV4dD48L3N2Zz4=;" parent="vf_a" vertex="1">
      <mxGeometry x="200" y="250" width="120" height="60"/>
    </mxCell>

    <!-- ISL Connection Core-A to Edge-A1 -->
    <mxCell id="isl_coreA_edgeA1" source="smc_core_a" target="smc_edge_a1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeColor=#FF6D00;strokeWidth=3;dashed=0;" parent="vf_a" edge="1">
      <mxGeometry relative="1">
        <mxPoint x="475" y="125" as="sourcePoint"/>
        <mxPoint x="260" y="250" as="targetPoint"/>
        <Array as="points">
          <mxPoint x="475" y="200"/>
          <mxPoint x="260" y="200"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <!-- Host Ports (Example: Oracle DB Server) -->
    <mxCell id="host_oracle1" value="&lt;b&gt;Oracle-DB1&lt;/b&gt;&lt;br&gt;21:00:00:24:FF:45:6A:BC" style="shape=cylinder;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;fillColor=#D5E8D4;strokeColor=#82B366;" parent="vf_a" vertex="1">
      <mxGeometry x="50" y="400" width="100" height="80"/>
    </mxCell>

    <!-- Host Connection -->
    <mxCell id="host1_conn" source="smc_edge_a1" target="host_oracle1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeColor=#666666;strokeWidth=2;dashed=0;" parent="vf_a" edge="1">
      <mxGeometry relative="1">
        <mxPoint x="200" y="310" as="sourcePoint"/>
        <mxPoint x="100" y="400" as="targetPoint"/>
      </mxGeometry>
    </mxCell>

    <!-- Storage Array (Example: EMC PowerMax) -->
    <mxCell id="stor_powermax1" value="&lt;b&gt;EMC PowerMax&lt;/b&gt;&lt;br&gt;50:00:12:34:56:78:90:12" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;fillColor=#F8CECC;strokeColor=#B85450;" parent="vf_a" vertex="1">
      <mxGeometry x="700" y="400" width="120" height="90"/>
    </mxCell>

    <!-- Storage Connection -->
    <mxCell id="stor1_conn" source="smc_core_a" target="stor_powermax1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeColor=#666666;strokeWidth=2;dashed=0;" parent="vf_a" edge="1">
      <mxGeometry relative="1">
        <mxPoint x="475" y="125" as="sourcePoint"/>
        <mxPoint x="760" y="400" as="targetPoint"/>
        <Array as="points">
          <mxPoint x="475" y="300"/>
          <mxPoint x="760" y="300"/>
        </Array>
      </mxGeometry>
    </mxCell>

    <!-- ==================== TLC SITE ==================== -->
    <mxCell id="tlc_site" value="TLC Site" style="swimlane;whiteSpace=wrap;html=1;fillColor=#E8F5E9;strokeColor=#388E3C;" parent="1" vertex="1">
      <mxGeometry x="1200" y="100" width="800" height="500"/>
    </mxCell>

    <!-- TLC Core Switch -->
    <mxCell id="tlc_core_a" value="&lt;b&gt;TLC-Core-A&lt;/b&gt;&lt;br&gt;(Domain 10)" style="shape=image;verticalLabelPosition=bottom;labelBackgroundColor=#ffffff;verticalAlign=top;aspect=fixed;image=data:image/svg+xml,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyMDAgMTAwIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI0RBRThGQyIgc3Ryb2tlPSIjNkM4RUJGIi8+PHRleHQgeD0iMTAwIiB5PSI1MCIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBhbGlnbm1lbnQtYmFzZWxpbmU9Im1pZGRsZSI+VENMLUNvcmU8L3RleHQ+PC9zdmc+;" parent="tlc_site" vertex="1">
      <mxGeometry x="100" y="50" width="150" height="75"/>
    </mxCell>

    <!-- Inter-Site ISL (Long Distance) -->
    <mxCell id="isl_smc_tlc" source="smc_core_a" target="tlc_core_a" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;strokeColor=#5D4037;strokeWidth=4;dashed=1;" parent="1" edge="1">
      <mxGeometry relative="1">
        <mxPoint x="550" y="125" as="sourcePoint"/>
        <mxPoint x="1200" y="87" as="targetPoint"/>
      </mxGeometry>
    </mxCell>

    <!-- ==================== ZONING ==================== -->
    <mxCell id="zone_db_prod" value="Oracle_DB_Zone" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#F8BBD0;strokeColor=#E91E63;dashed=1;opacity=30;" parent="Zoning" vertex="1">
      <mxGeometry x="150" y="350" width="600" height="150" as="geometry"/>
    </mxCell>
  </diagram>
</mxfile>
```

---

### **Key Features Included**
1. **Physical Layout**:
   - Separate containers for SMC/TLC sites
   - X7-8 director switches with custom SVG icons

2. **Virtual Fabrics**:
   - Dedicated swimlane for VF_A (VF_B would follow same pattern)
   - Color-coded borders (orange for VF_A)

3. **Device Details**:
   - **Hosts**: Oracle DB server with WWPN
   - **Storage**: EMC PowerMax array with WWN
   - Port-level connections shown

4. **Inter-Site Connectivity**:
   - Dashed brown line for long-distance ISL
   - Clear core-to-core linkage

5. **Zoning Overlay**:
   - Pink transparent zone for Oracle DB
   - Toggle visibility via layers

---

### **How to Use This Template**
1. **Import into draw.io**:
   - Create new diagram → File → Open From → XML...
   - Paste the entire XML

2. **Customize**:
   - Duplicate elements for VF_B
   - Adjust coordinates for layout balance
   - Add your actual WWPNs/WWNs

3. **Extend**:
   ```xml
   <!-- Example: Add more hosts -->
   <mxCell id="host_oracle2" value="Oracle-DB2" style="..." parent="vf_a">
     <mxGeometry x="50" y="500" width="100" height="80"/>
   </mxCell>
   ```

---

### **Pro Tips**
1. **For Scripted Generation**:
   ```python
   # Python snippet to auto-generate host entries
   hosts = [
       {"name": "Oracle-DB2", "wwn": "21:00:00:24:FF:4A:2D:EF", "x": 50, "y": 500}
   ]
   
   for i, host in enumerate(hosts):
       print(f'<mxCell id="host_{i}" value="{host["name"]}&lt;br&gt;{host["wwn"]}" style="..." parent="vf_a">')
       print(f'  <mxGeometry x="{host["x"]}" y="{host["y"]}" width="100" height="80"/>')
       print('</mxCell>')
   ```

2. **Visual Hierarchy**:
   - Core switches at top
   - Edge switches middle
   - Hosts/storage at bottom

3. **Layer Control**:
   - Toggle "Zoning" layer to show/hide zones
   - Hide "Virtual_Fabrics" to see physical only

Would you like me to add specific elements like:
- Trunk group visualizations?
- FICON traffic markings?
- Oversubscription warnings?
