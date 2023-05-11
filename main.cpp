#include <glob.h>
#include <iostream>
#include <fstream>

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/mman.h>
#include <sys/times.h>
#include <vector>
#include <chrono>

using namespace std;

int main()
{
	glob_t glob_result;
	glob("/sys/kernel/debug/adsprpc/snpe*",GLOB_TILDE,NULL,&glob_result);
	while(glob_result.gl_pathc == 0)
	{
		cout << "waiting for snpe debugFS" << endl;
		glob("/sys/kernel/debug/adsprpc/qnn*",GLOB_TILDE,NULL,&glob_result);
	}
	  
    char *filePath = glob_result.gl_pathv[0];
	cout << "FileName: " << filePath  << endl;
	
	struct timeval start_time, stop_time;
     
 
  
	vector<string> buffer;
    while (glob_result.gl_pathc == 1)
    {
		//long T1 = times(&start_time);
		gettimeofday(&start_time,0);
		std::ifstream is(filePath);  
		if(is){
//			cout << "file read successfully" << endl;
		}
		else{
			cout << "file reading failed" << endl;
			break;
		}
        if (is) {
			
			string line;
			while (getline(is, line))
			{
				//cout << line << endl;
				buffer.push_back(line);
			}
			   
        }
		is.close();
		//long T2 = times(&stop_time);
		gettimeofday(&stop_time,0);
		//long sec = stop_time.tv_sec - start_time.tv_sec;
		//long micro = stop_time.tv_usec - start_time.tv_usec;
		long sec = start_time.tv_sec;
		long micro =start_time.tv_usec;
		double elapsed = sec + micro * 1e-6;
		buffer.push_back(to_string(elapsed));
		//printf("timeStamp:- %.6f\n", elapsed );	
			
	}
	
	for(int i=0;i<buffer.size();i++)
    {
		cout << "timeStamp:-" << buffer[i] << endl;
	}
	
	// Printing each new line separately
	//copy(buffer.begin(), buffer.end(), ostream_iterator<string>(cout, "\n"));
	/*fstream file;
    file.open("DebugFSfile.txt",ios_base::out);
 
    for(int i=0;i<buffer.size();i++)
    {
        file<<buffer[i]<<endl;
    }
 
    file.close();
	*/
	
	/*
	fstream file;
    file.open("/data/local/tmp/exec/DebugFSfile.txt",ios_base::out);
 
    ostream_iterator<string> out_itr(file, "\n");
    copy(buffer.begin(), buffer.end(), out_itr);
 
    file.close();
	*/

return 0;
}


