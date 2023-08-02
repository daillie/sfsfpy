def script_patch(address: str, original_bytes: list, new_bytes: list, name: str) -> str:
    return """                
        const inAddr = ptr('%s');
        const bytesToFind = toMemArray(%s)
        const bytesLength = bytesToFind.length;
        const newBytes = toMemArray(%s);
        const name = '%s';
        
        var currentBytesRaw = new Uint8Array(inAddr.readByteArray(64));
        var currentBytes = [];
        
        for(var i = 0; i < bytesLength; i++) {                                                            
            var byte = currentBytesRaw[i].toString(16).toUpperCase();                
            byte = byte.length == 1 ?'0x0' + byte : '0x'+byte;
        
            currentBytes.push(byte);
        }
        
        if (arraysEqual(bytesToFind, currentBytes))
            if (patchAddress(inAddr, newBytes))
                send('[+] ' + name + ' patched');
            else
                send('[-] ' + name + 'patch err');
        else if (arraysEqual(newBytes, currentBytes.slice(0, newBytes.length )))
            send( '[!] ' + name + ' already patched' );
        else
            send("[-] err, can't find " + name );
        
        
        function patchAddress(address, bytesStr){                    
            if (!Memory.protect(address, 4096, 'rwx'))
                return false                
            try{
                Memory.writeByteArray(address, bytesStr);
            } catch(e)
            {
                console.log('cannot write ' + bytesStr + ' at address: ' + address);
                return false;
            }            
            return true;                    
        }   
        
        function arraysEqual(a, b) {
            if (a === b) return true;
            if (a == null || b == null) return false;
            if (a.length !== b.length) return false;
        
            for (var i = 0; i < a.length; ++i) {
                if (a[i] !== b[i]) return false;
            }
            return true;
        }
        
        function toMemArray(bytesArray){
            return bytesArray.map( x => !x.includes('0x')
             ? '0x' + x.toUpperCase() 
             : '0x' + x.replace('0x','').toUpperCase())
        }
        """ % (address, original_bytes, new_bytes, name)


def script_get_module_base(module_name: str) -> str:
    return """
        var module = Process.getModuleByName("%s");
        var baseAddress = module.base.toString();
        send(baseAddress);
        """ % module_name


def script_scan_patch(scan_pattern: str, new_bytes: list, module_name: str, name: str) -> str:
    return """          
        const pattern = "%s";
        const moduleName = "%s";        
        const newBytes = toMemArray(%s);                        
        const name = '%s';
                        
        function main(){
            var m = Process.getModuleByName(moduleName);    
            const results = Memory.scanSync(m.base, m.size, pattern);
            
            if (results.length == 0){
                send("[-] " + name + " was not found");
                return;
            }            
            if (patchAddress(results[0].address, newBytes))
                send('[+]'+ name + ' patched at address: '+ results[0].address.toString());
            else
                send('[-]'+ name + 'cannot be patched');
        }
                    
        function toMemArray(bytesArray){
            return bytesArray.map( x => !x.includes('0x')
             ? '0x' + x.toUpperCase() 
             : '0x' + x.replace('0x','').toUpperCase())
        }
        
        function patchAddress(address, bytesStr){                    
            if (!Memory.protect(address, 4096, 'rwx'))
                return false                
            try{
                Memory.writeByteArray(address, bytesStr);
            } catch(e)
            {
                console.log('cannot write ' + bytesStr + ' at addr: ' + address);
                return false;
            }            
            return true;                    
        }   
        
        main();
        """ % (scan_pattern, module_name, new_bytes, name)
