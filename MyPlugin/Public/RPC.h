// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "async_server.h"

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "RPC.generated.h"

UCLASS()
class MYPLUGIN_API ARPC : public AActor
{
	GENERATED_BODY()
	
public:	
	// Sets default values for this actor's properties
	ARPC();

protected:
	// Called when the game starts or when spawned
	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason);

public:	
	// Called every frame
	virtual void Tick(float DeltaTime) override;

	TFunction< void() > MyTaskFunc;

	ServerImpl* server;

};
