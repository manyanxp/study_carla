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
        // コンストラクタで指定された関数を実行
        Work();
    }

    FORCEINLINE TStatId GetStatId() const
    {
        RETURN_QUICK_DECLARE_CYCLE_STAT(FAsyncExecTask, STATGROUP_ThreadPoolAsyncTasks);
    }

private:
    TFunction<void()> Work;
};
