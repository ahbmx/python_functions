# Restricting SRDF Operations to 2 Device Groups in a Host Using SYMUTH

To restrict SRDF operations to only 2 device groups (not RDF groups) within a host using SYMUTH, you'll need to configure device group-level authorization. Here's how to implement this:

## Implementation Steps

1. **Identify the Device Groups**:
   First determine which 2 device groups you want to allow SRDF operations for.

2. **Configure SYMUTH Authorization**:
   Use the following command to restrict access:

   ```
   symauth -sid <SymmID> add -type host -host <HostName> -restrict_dg <DeviceGroup1>,<DeviceGroup2>
   ```

   Where:
   - `<SymmID>` is your Symmetrix ID
   - `<HostName>` is the host name you're restricting
   - `<DeviceGroup1>` and `<DeviceGroup2>` are the two device groups you want to allow

3. **For SRDF-Specific Operations**:
   If you want to further restrict to SRDF operations only within these device groups:
   ```
   symauth -sid <SymmID> add -type host -host <HostName> -restrict_dg <DeviceGroup1>,<DeviceGroup2> -restrict_rdf
   ```

4. **Verify the Configuration**:
   Check the restrictions with:
   ```
   symauth -sid <SymmID> list -type host -host <HostName>
   ```

## Important Notes

- This will restrict the host to only see and manage the specified device groups
- The `-restrict_rdf` option ensures these restrictions apply specifically to SRDF operations
- All other device groups will be invisible/unauthorized from this host
- You may need Storage Administrator privileges to modify these settings

## Example

For Symmetrix ID 000123456789, host "SRDF_Server1", allowing only device groups "DG_PROD_A" and "DG_PROD_B" for SRDF operations:

```
symauth -sid 000123456789 add -type host -host SRDF_Server1 -restrict_dg DG_PROD_A,DG_PROD_B -restrict_rdf
```

Would you like me to provide any additional details about device group restrictions or SRDF-specific authorization?
