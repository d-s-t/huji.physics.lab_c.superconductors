function fname=nextAvailableFilename(path,fnamePattern,extension)
    filenameAvailable=false;
    i=1;
    while (~filenameAvailable)
        fname=sprintf('%s%s_%d.%s',path,fnamePattern,i,extension);
        if (exist(fname,'file')==0)
            filenameAvailable=true;
        end
        i=i+1;
    end
end