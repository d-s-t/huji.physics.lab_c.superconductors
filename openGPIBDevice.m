function devOut=openGPIBDevice(vendor,boardIndex,primaryAddress)
    obj1 = instrfind('Type', 'gpib', 'BoardIndex', boardIndex, 'PrimaryAddress', primaryAddress, 'Tag', '');
    if isempty(obj1)
        obj1 = gpib(vendor, boardIndex, primaryAddress);
    else
       fclose(obj1);
       obj1 = obj1(1);
    end
    fopen(obj1);
    devOut=obj1;
end