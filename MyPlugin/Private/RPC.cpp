// Fill out your copyright notice in the Description page of Project Settings.


#include "RPC.h"
#include "async_exec_task.h"
#include "Runtime/Engine/Classes/Engine/StaticMeshActor.h"

// Sets default values
ARPC::ARPC()
{
 	// Set this actor to call Tick() every frame.  You can turn this off to improve performance if you don't need it.
	PrimaryActorTick.bCanEverTick = true;

}

// Called when the game starts or when spawned
void ARPC::BeginPlay()
{
	Super::BeginPlay();

	TSubclassOf<AEmitter> findClass;
	findClass = AEmitter::StaticClass();
	TArray<AActor*> emitters;
	UGameplayStatics::GetAllActorsOfClass(GetWorld(), findClass, emitters);


	server = new ServerImpl(emitters);

	MyTaskFunc = [this] {
		this->server->Run();
	};

	auto async_task = new FAutoDeleteAsyncTask<FAsyncExecTask>(MyTaskFunc);
	async_task->StartBackgroundTask();
	
}

// Called every frame
void ARPC::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);


}

void ARPC::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Super::EndPlay(EndPlayReason);

	delete server;
}