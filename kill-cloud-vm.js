const gce = require('@google-cloud/compute')({
    projectId: 'ml-sandbox-1-191918'
    });
    const zone = gce.zone('us-east1-c');
    console.log('Getting your VMs...');
    zone.getVMs().then((data) => {
    data[0].forEach((vm) => {
    console.log('Found a VM called', vm.name);
    console.log('Stopping', vm.name, '....');
    vm.stop((err, operation) => {
        operation.on('complete', (err) => {
            console.log('stopped', vm.name)
        });
    
    });
    });
    console.log('Done.');
    });