{
  description = "研究计划草稿技能及固定运行环境（苹果芯片 Mac、Codex）";

  # 全部直接能力和共享安装器来自这一输入的原锁定图。
  inputs.contact.url = "github:ScholarWorkflow/professor-contact/ad096fe31a4b5694cbe47a40f37b621435e1eeec";

  outputs = { self, contact }:
    let
      system = "aarch64-darwin";
      pkgs = contact.inputs.nixpkgs.legacyPackages.${system};
      shared = contact.inputs.agent-env-nix.lib;
      research = contact.inputs.professor-research;
      base = contact.inputs.base-skills;
      source = research.inputs.browser-pdf-tools.inputs.source-access-skills;

      products = import ./nix/research-proposal.nix {
        inherit pkgs;
        inherit (shared) mkAgentPackage mkProject;
        contactRuntime = contact.packages.${system}.professor-contact-runtime;
        visionGlance = base.apps.${system}.vision-glance.program;
        agentDependencies = [
          contact.packages.${system}.professor-contact
          research.packages.${system}.professor-collector
          research.packages.${system}.professor-topic-clustering
          source.packages.${system}.duckduckgo-search
          source.packages.${system}.yahoo-japan-search
          base.packages.${system}.vision-tools
        ];
      };
    in
    {
      packages.${system} = {
        research-proposal-runtime = products.runtime;
        research-proposal = products.package;
        research-proposal-environment = products.project;
        research-proposal-activate = shared.mkCachedActivation {
          inherit pkgs;
          environment = products.project;
          name = "research-proposal-activate";
        };
      };
    };
}
