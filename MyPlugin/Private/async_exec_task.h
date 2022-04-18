#pragma once

#include "Async/AsyncWork.h"

class FAsyncExecTask : public FNonAbandonableTask
{
    friend class FAutoDeleteAsyncTask<FAsyncExecTask>;

public:
    FAsyncExecTask(TFunction<void()> InWork)
        : Work(InWork)
    {
    }

    void DoWork()
    {
        // �R���X�g���N�^�Ŏw�肳�ꂽ�֐������s
        Work();
    }

    FORCEINLINE TStatId GetStatId() const
    {
        RETURN_QUICK_DECLARE_CYCLE_STAT(FAsyncExecTask, STATGROUP_ThreadPoolAsyncTasks);
    }

private:
    TFunction<void()> Work;
};
