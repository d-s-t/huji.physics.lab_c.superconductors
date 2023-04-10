function measValue=readMeas(device)
    measValue=cell2mat(textscan(fscanf(device),'%f'));
end