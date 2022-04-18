// Copyright Epic Games, Inc. All Rights Reserved.

using System.IO;
using UnrealBuildTool;

public class MyPlugin : ModuleRules
{
	private string ThirdPartyDirectory
	{
		get
		{
			return Path.GetFullPath(Path.Combine(ModuleDirectory, "../../ThirdParty/"));
		}
	}

	private string ThirdPartyLibrariesDirectory
	{
		get
		{
			return Path.Combine(ThirdPartyDirectory, "libs");
		}
	}

	public MyPlugin(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;
		
		PublicIncludePaths.AddRange(
			new string[] {
				// ... add public include paths required here ...
			}
			);
				
		
		PrivateIncludePaths.AddRange(
			new string[] {
				// ... add other private include paths required here ...
			}
			);
			
		
		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
				// ... add other public dependencies that you statically link with here ...
			}
			);
			
		
		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"Slate",
				"SlateCore",
				// ... add private dependencies that you statically link with here ...	
			}
			);
		
		
		DynamicallyLoadedModuleNames.AddRange(
			new string[]
			{
				// ... add any modules that your module loads dynamically here ...
			}
			);

		PublicDefinitions.Add("GOOGLE_PROTOBUF_NO_RTTI");
		// PublicDefinitions.Add("GPR_FORBID_UNREACHABLE_CODE");
		PublicDefinitions.Add("GRPC_ALLOW_EXCEPTIONS=0");

		PublicIncludePaths.Add(Path.Combine(ThirdPartyDirectory, "inc"));

		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "address_sorting.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "cares.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "gpr.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "grpc_unsecure.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "grpc++_unsecure.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "libprotobuf.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "upb.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_base.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_malloc_internal.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_raw_logging_internal.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_spinlock_wait.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_throw_delegate.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_time.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_time_zone.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_graphcycles_internal.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_synchronization.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_cord.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_str_format_internal.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_strings.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_strings_internal.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_status.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_statusor.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_bad_optional_access.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_stacktrace.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_symbolize.lib"));
		PublicAdditionalLibraries.Add(Path.Combine(ThirdPartyLibrariesDirectory, "absl_int128.lib"));

		AddEngineThirdPartyPrivateStaticDependencies(Target, "zlib");
	}
}
