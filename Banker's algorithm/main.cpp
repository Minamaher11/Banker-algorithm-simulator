#include<iostream>
#include <vector>
using namespace std;


//Banker's Algorithm Class
class Banker 
{
private:
    int nProccessNumber; // Number of processes
    int nResourceNumber; // Number of resources

    vector<vector<int>> vAllocation;//allocation matrix
    vector<vector<int>> vMaxNeed;//maxNeed matrix
    vector<vector<int>> vNeed;//need matrix
    vector<int> vAvailable;//available resources

//for use on main and other functions,classes
public:
    //constructor
    Banker(int p, int r) 
    {
        nProccessNumber = p;
        nResourceNumber = r;
        vAllocation.resize(nProccessNumber, vector<int>(nResourceNumber));
        vMaxNeed.resize(nProccessNumber, vector<int>(nResourceNumber));
        vNeed.resize(nProccessNumber, vector<int>(nResourceNumber));
        vAvailable.resize(nResourceNumber,0);
    }
    
    //for input allocation matrix
    void InputAllocation()
    {
        cout<<endl;
        cout << "Enter Allocation Matrix:\n";
        for(int i=0;i<nProccessNumber;i++)
            for(int j=0;j<nResourceNumber;j++)
                cin >> vAllocation[i][j];
    }
    //max need function
    void InputMax() {
        cout << "\nEnter Max Matrix:\n";
        for(int i=0;i<nProccessNumber;i++)
            for(int j=0;j<nResourceNumber;j++)
                cin >> vMaxNeed[i][j];
    }
    //avilable recourses function
    void InputAvailable() {
        cout << "\nEnter Available Resources:\n";
        for(int j=0;j<nResourceNumber;j++)
            cin >> vAvailable[j];
    }
    //calculation need function
    void CalculateNeed() {
        for(int i=0;i<nProccessNumber;i++)
            for(int j=0;j<nResourceNumber;j++)
                vNeed[i][j] = vMaxNeed[i][j] - vAllocation[i][j];
    }
    //show state function
    //عدل شويه
    void ShowState() {
        cout << "\nAvailable: ";
        for(int j=0;j<nResourceNumber;j++)
            cout << vAvailable[j] << " ";
        cout << "\nAllocation Matrix:\n";
        for(int i=0;i<nProccessNumber;i++){
            for(int j=0;j<nResourceNumber;j++)
                cout << vAllocation[i][j] << " ";
            cout << endl;
        }
        cout << "Max Matrix:\n";
        for(int i=0;i<nProccessNumber;i++){
            for(int j=0;j<nResourceNumber;j++)
                cout << vMaxNeed[i][j] << " ";
            cout << endl;
        }
        cout << "Need Matrix:\n";
        for(int i=0;i<nProccessNumber;i++){
            for(int j=0;j<nResourceNumber;j++)
                cout << vNeed[i][j] << " ";
            cout << endl;
        }
    }

    // Safety Check
    bool isSafe() {
        vector<int> vWork = vAvailable;
        vector<bool> vFinish(nProccessNumber,false);
        vector<int> vSafeSequence;

        for(int k=0;k<nProccessNumber;k++)
        {
            bool found=false;
            for(int i=0;i<nProccessNumber;i++)
            {
                if(!vFinish[i])
                {
                    bool canRun=true;
                    for(int j=0;j<nResourceNumber;j++){
                        if(vNeed[i][j]>vWork[j])
                        {
                            canRun=false;
                            break;
                        }
                    }
                    if(canRun)
                    {
                        for(int j=0;j<nResourceNumber;j++)
                            vWork[j]+=vAllocation[i][j];
                        vFinish[i]=true;
                        vSafeSequence.push_back(i);
                        found=true;
                    }
                }
            }
            if(!found)
            {
                cout << "\nSystem is NOT SAFE.\n";
                return false;
            }
        }

        cout << "\nSystem is SAFE.\nSafe Sequence: ";
        for(int i : vSafeSequence)
            cout << "P" << i << " ";
        cout << endl;

        return true;
    }

    bool requestResources(int p, vector<int> vRequest)
    {
        // تحقق إذا الطلب <= Need
        for(int j=0;j<nResourceNumber;j++)
        {
            if(vRequest[j] > vNeed[p][j])
            {
                cout << "Error: Request exceeds process maximum demand.\n";
                return false;
            }
        }
        // تحقق إذا الطلب <= Available
        for(int j=0;j<nResourceNumber;j++)
        {
            if(vRequest[j] > vAvailable[j])
            {
                cout << "Resources not available, process must wait.\n";
                return false;
            }
        }

        // Tentative allocation
        vector<int> tempAvailable = vAvailable;
        vector<vector<int>> tempAlloc = vAllocation;
        for(int j=0;j<nResourceNumber;j++)
        {
            tempAvailable[j] -= vRequest[j];
            tempAlloc[p][j] += vRequest[j];
        }

        // حساب Need مؤقت
        vector<vector<int>> tempNeed = vMaxNeed;
        for(int i=0;i<nResourceNumber;i++)
        {
            tempNeed[p][i] = vMaxNeed[p][i] - tempAlloc[p][i];
        }

        // Safety check مؤقت
        vector<int> work = tempAvailable;
        vector<bool> finish(nProccessNumber,false);
        for(int k=0;k<nProccessNumber;k++)
        {
            bool found=false;
            for(int i=0;i<nProccessNumber;i++)
            {
                if(!finish[i])
                {
                    bool canRun=true;
                    for(int j=0;j<nResourceNumber;j++)
                    {
                        if(tempNeed[i][j] > work[j])
                        {
                            canRun=false;
                            break;
                        }
                    }
                    if(canRun)
                    {
                        for(int j=0;j<nResourceNumber;j++)
                            work[j]+=tempAlloc[i][j];
                        finish[i]=true;
                        found=true;
                    }
                }
            }
            if(!found)
                break;
        }

        bool safe=true;
        for(int i=0;i<nProccessNumber;i++)
            if(!finish[i]) safe=false;

        if(safe){
            // اعتمد التغيير فعلياً
            vAvailable = tempAvailable;
            vAllocation = tempAlloc;
            vNeed = tempNeed;
            cout << "Request granted. System remains SAFE.\n";
            return true;
        } else {
            cout << "Request denied. Granting would lead to UNSAFE state.\n";
            return false;
        }
    }


};





int main() {
    int P,R;
    cout << "Enter number of processes: ";
    cin >> P;
    cout << "Enter number of resources: ";
    cin >> R;

    Banker b(P,R);

    b.InputAllocation();
    b.InputMax();
    b.InputAvailable();
    b.CalculateNeed();

    while(true){
        cout << "\nMenu:\n1. Show State\n2. Check Safety\n3. Request Resources\n4. Exit\nChoice: ";
        int choice;
        cin >> choice;

        if(choice==1)
        {
            b.ShowState();
        } 
        else if(choice==2)
        {
            b.isSafe();
        } 
        else if(choice==3)
        {
            int p;
            cout << "Enter process number: ";
            cin >> p;
            vector<int> request(R);
            cout << "Enter request vector: ";
            for(int j=0;j<R;j++)
                cin >> request[j];
            b.requestResources(p, request);
        } 
        else if(choice==4)
        {
            cout << "Exiting...\n";
            break;
        } 
        else 
        {
            cout << "Invalid choice.\n";
        }
    }

    return 0;
}
