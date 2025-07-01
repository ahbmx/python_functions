You're absolutely right! Let me provide the correct **Brocade/Broadcom Fabric OS (X7-8 Director)** commands for monitoring health and capacity.  

---

# **Broadcom X7-8 Director (Brocade Fabric OS) Cheat Sheet**  
**Useful commands for monitoring capacity, health, and performance.**  

---

## **1. General Director Status & Health**  

### **Director & Switch Information**  
- Show chassis information (model, firmware, uptime):  
  ```shell
  chassisShow
  ```
- Display switch status and health:  
  ```shell
  switchShow
  ```
- Check firmware version:  
  ```shell
  version
  ```

### **Environmental Monitoring**  
- Show temperature, voltage, and fan status:  
  ```shell
  sensorshow
  ```
- Check power supply status:  
  ```shell
  psmShow
  ```
- View hardware errors:  
  ```shell
  errdump
  ```

---

## **2. Port & Traffic Monitoring**  

### **Port Status & Statistics**  
- List all ports and their status:  
  ```shell
  portShow
  ```
- Show detailed port statistics (errors, traffic):  
  ```shell
  portStatsShow
  ```
- Reset port counters:  
  ```shell
  portstatsclear
  ```
- Check port buffer usage:  
  ```shell
  portbufusageShow
  ```

### **Traffic & Performance**  
- Monitor real-time traffic per port:  
  ```shell
  portperfShow
  ```
- Check ISL (Inter-Switch Link) utilization:  
  ```shell
  islshow
  ```
- Display traffic flow statistics:  
  ```shell
  trafficShow
  ```

---

## **3. Capacity & Resource Usage**  

### **Zone & Fabric Capacity**  
- Show active zoneset:  
  ```shell
  zoneshow
  ```
- Check fabric nameserver (device count):  
  ```shell
  nsShow
  ```
- Display registered devices:  
  ```shell
  nsshow
  ```

### **Buffer & Resource Allocation**  
- Show buffer credit usage:  
  ```shell
  buffercmdshow
  ```
- Check ASIC resource allocation:  
  ```shell
  resourceShow
  ```

---

## **4. Error & Diagnostic Commands**  

### **Logs & Troubleshooting**  
- View system logs:  
  ```shell
  logsShow
  ```
- Check recent errors:  
  ```shell
  errShow
  ```
- Capture support data (for Broadcom TAC):  
  ```shell
  supportSave
  ```

### **Fabric Stability & Diagnostics**  
- Check fabric stability (RSCN, errors):  
  ```shell
  fabricShow
  ```
- Test link connectivity:  
  ```shell
  ping [WWN or IP]
  ```
- Verify trunking status:  
  ```shell
  trunkshow
  ```

---

## **5. Firmware & Maintenance**  

### **Firmware & Licensing**  
- Check license status:  
  ```shell
  licenseShow
  ```
- Upgrade firmware (requires reboot):  
  ```shell
  firmwareDownload
  firmwareCommit
  ```

### **Reboot & Recovery**  
- Reboot the director:  
  ```shell
  reboot
  ```
- Factory reset (use with caution):  
  ```shell
  fastboot
  fastbootConfigDefault
  ```

---

### **Summary**  
- **Health:** `chassisShow`, `sensorshow`, `psmShow`  
- **Ports:** `portShow`, `portStatsShow`, `portperfShow`  
- **Capacity:** `nsShow`, `buffercmdshow`, `resourceShow`  
- **Errors:** `errShow`, `logsShow`, `supportSave`  

This cheat sheet covers the most useful **Broadcom X7-8 Director (Brocade Fabric OS)** commands for monitoring and troubleshooting. Let me know if you need more details on any command! 🚀
