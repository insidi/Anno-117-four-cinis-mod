using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using System.Text;
using System.Text.Json;
using System.Xml;
using FileDBSerializing;
using FileDBReader.src.XmlRepresentation;
using RDAExplorer;

if (args.Length < 3) throw new ArgumentException("roundtrip|resize|template input output [size]");
if(args[0]=="pack")
{
    // RDA 2.2 container convention used by AnnoMapEditorRenew/Anno117ModWriter.cs.
    using var stream=File.OpenRead(args[1]);
    using var binary=new BinaryReader(stream);
    using var reader=new RDAReader();
    var folder=new RDAFolder(FileHeader.Version.Version_2_2);
    reader.rdaFolder=folder;
    var entry=new DirEntry { filename=RDAFile.FileNameToRDAFileName("gamedata.data",""),offset=0,compressed=(ulong)stream.Length,filesize=(ulong)stream.Length,timestamp=0 };
    var block=new BlockInfo { flags=0,fileCount=1,directorySize=(ulong)stream.Length,decompressedSize=(ulong)stream.Length,nextBlock=0 };
    folder.AddFiles(new List<RDAFile>{RDAFile.FromUnmanaged(FileHeader.Version.Version_2_2,entry,block,binary,null)});
    RDABlockCreator.FileType_CompressedExtensions.Add(".data");
    new RDAWriter(folder).Write(args[2],FileHeader.Version.Version_2_2,true,reader,null);
    Console.WriteLine("Packed compressed gamedata.data: "+new FileInfo(args[2]).Length+" bytes");
    return;
}
if(args[0]=="footprints")
{
    var rows=new List<object>();
    foreach(var file in Directory.GetFiles(args[1],"*.a7minfo",SearchOption.AllDirectories))
    {
        var doc=Read(file);
        var size=((Attrib)doc.Roots.Single(n=>n.Name=="MapSize")).Content;
        rows.Add(new{ file=Path.GetFileName(file), width=BitConverter.ToInt32(size),height=BitConverter.ToInt32(size,4) });
    }
    File.WriteAllText(args[2],JsonSerializer.Serialize(rows,new JsonSerializerOptions{WriteIndented=true}));
    return;
}
var input = Read(args[1]);
if (args[0] == "inspect-area")
{
    var root=(Tag)input.Roots.Single(n=>n.Name=="GameSessionManager");
    var grid=(Tag)Find(root,"AreaIDs");
    var counts=new Dictionary<ushort,long>();
    var examples=new List<string>();
    foreach(var block in grid.Children.OfType<Tag>().Where(n=>n.Name=="block").Skip(1))
    foreach(var attr in block.Children.OfType<Attrib>().Where(a=>a.Name=="values" || a.Name=="default"))
    {
        for(int i=0;i<attr.Content.Length;i+=2){var val=BitConverter.ToUInt16(attr.Content,i); counts[val]=counts.GetValueOrDefault(val)+1;}
        if(attr.Content.Any(b=>b!=0) && examples.Count<8) examples.Add(string.Join(" ",block.Children.OfType<Attrib>().Select(a=>a.Name+"="+Hex(a.Content.Take(24).ToArray()))));
    }
    Console.WriteLine(JsonSerializer.Serialize(counts));
    examples.ForEach(Console.WriteLine);
    return;
}
if (args[0] == "roundtrip")
{
    Save(input, args[2]);
    Equal(input.Roots, Read(args[2]).Roots);
    Console.WriteLine("PASS: every FileDB node and payload survived roundtrip");
}
else if (args[0] == "resize")
{
    int size = int.Parse(args[3]);
    if (size % 64 != 0 || size < 2688) throw new ArgumentException("Invalid size");
    var root = (Tag)input.Roots.Single(n => n.Name == "GameSessionManager");
    Set(root, "SessionSettings/PlayableArea", Ints(20, 20, size - 20, size - 20));
    var grid = (Tag)Find(root, "AreaIDs");
    int oldSize = BitConverter.ToInt32(((Attrib)Find(grid,"x")).Content);
    const int offset = 1024;
    Require(oldSize == 2688 && size == 4096, "Unsupported source/target dimensions");
    Set(grid, "x", Ints(size)); Set(grid, "y", Ints(size));
    var blocks = grid.Children.OfType<Tag>().Where(n => n.Name == "block").ToList();
    Require(BitConverter.ToInt16(((Attrib)Find(blocks[0], "x")).Content) == 16, "Unexpected sparse grid stride");
    Require(((Attrib)Find(blocks[0],"default")).Content.All(b=>b==0),"Unexpected default area ID");
    int Coord(Tag t,string name) => t.Children.OfType<Attrib>().FirstOrDefault(a=>a.Name==name) is Attrib a ? BitConverter.ToInt16(a.Content) : 0;
    Require(blocks.Last().Children.Count == 1 && ((Attrib)Find(blocks.Last(),"mode")).Content.SequenceEqual(new byte[]{0}),"Missing area grid terminator");
    var sourceBlocks=blocks.Skip(1).SkipLast(1).ToDictionary(b=>(Coord(b,"x"),Coord(b,"y")));
    grid.Children.RemoveAll(n => n.Name == "block" && n != blocks[0]);
    // Sparse mode supplies zero for omitted blocks. Retain every source block and shift its key.
    foreach(var pair in sourceBlocks)
    {
        var block = (Tag)Clone(pair.Value, grid);
        foreach(var coord in new[]{("x",pair.Key.Item1+offset),("y",pair.Key.Item2+offset)})
        {
            Require(coord.Item2>=offset && coord.Item2<offset+oldSize,"Invalid source block coordinate");
            if(!block.Children.Any(c=>c.Name==coord.Item1)) block.AddChild(Clone(Find(blocks[0],coord.Item1),block));
            Set(block,coord.Item1,BitConverter.GetBytes((short)coord.Item2));
        }
        grid.AddChild(block);
    }
    grid.AddChild(Clone(blocks.Last(),grid));
    Set(root, "TerrainManager/WorldSize", Ints(size, size));
    foreach (var name in new[] { "HeightMap", "DisplacementHeightMap" })
    {
        var map = (Tag)Find(root, "TerrainManager/" + name);
        var payload = (Attrib)Find(map, "HeightMap");
        byte a = payload.Content[0], b = payload.Content[1];
        int oldWidth=BitConverter.ToInt32(((Attrib)Find(map,"Width")).Content);
        Require(oldWidth==oldSize*2+1 && payload.Content.Length==oldWidth*oldWidth*2,"Unexpected height grid");
        int width = size * 2 + 1;
        Set(map, "Width", Ints(width)); Set(map, "Height", Ints(width));
        var resized = new byte[checked(width * width * 2)];
        for (int i = 0; i < resized.Length; i += 2) { resized[i] = a; resized[i + 1] = b; }
        for(int y=0;y<oldWidth;y++) Buffer.BlockCopy(payload.Content,y*oldWidth*2,resized,((y+offset*2)*width+offset*2)*2,oldWidth*2);
        payload.Content = resized;
    }
    foreach (var name in new[] { "Water", "RiverGrid", "FordGrid" })
    {
        var map = (Tag)Find(root, "WorldManager/" + name);
        var old=((Attrib)Find(map,"bits")).Content;
        Require(old.Length==oldSize*oldSize/8,"Unexpected bit grid size");
        Set(map, "x", Ints(size)); Set(map, "y", Ints(size));
        var bits=new byte[size*size/8];
        for(int y=0;y<oldSize;y++) Buffer.BlockCopy(old,y*oldSize/8,bits,((y+offset)*size+offset)/8,oldSize/8);
        Set(map, "bits", bits);
    }
    var env = (Tag)Find(root, "WorldManager/EnvironmentGrid/EnvironmentGRid");
    var oldEnv=((Attrib)Find(env,"val")).Content;
    Require(oldEnv.Length==oldSize*oldSize/16,"Unexpected environment grid size");
    Set(env, "x", Ints(size / 4)); Set(env, "y", Ints(size / 4));
    var newEnv=new byte[size*size/16];
    for(int y=0;y<oldSize/4;y++) Buffer.BlockCopy(oldEnv,y*(oldSize/4),newEnv,(y+offset/4)*(size/4)+offset/4,oldSize/4);
    Set(env, "val", newEnv);
    Save(input, args[2]);
    Equal(input.Roots, Read(args[2]).Roots);
    Console.WriteLine($"PASS: source grids shifted +1024/+1024 and padded to {size}; other managers preserved; binary roundtrip verified");
}
else if (args[0] == "template")
{
    var xml = new FileDbXmlConverter().ToXml(input);
    var map = xml.SelectSingleNode("/Content/MapTemplate")!;
    Require(Decode(map["Size"]!.InnerText).SequenceEqual(new[] {2688,2688}), "Unexpected source dimensions");
    var slots = map.SelectNodes("TemplateElement")!.Cast<XmlElement>().ToList();
    var original = slots.Single(n => n["Element"]!["MapFilePath"] is XmlElement p && Encoding.Unicode.GetString(Convert.FromHexString(p.InnerText)).Contains("roman_dlc01_island_continental_01"));
    foreach (var slot in slots.Where(s => s != original))
    {
        var position = slot["Element"]!["Position"]!;
        var xy = Decode(position.InnerText);
        position.InnerText = Hex(Ints(xy[0] + 1024, xy[1] + 1024));
    }
    map["Size"]!.InnerText = Hex(Ints(4096, 4096));
    map["PlayableArea"]!.InnerText = Hex(Ints(20, 20, 4076, 4076));
    map["InitialPlayableArea"]!.InnerText = Hex(Ints(1044, 1044, 3044, 3044));
    map["EnlargementOffset"]!.InnerText = Hex(Ints(1024, 1024));
    var positions = new[] { ("North",3200,3200), ("East",3200,128), ("South",128,128), ("West",128,3200) };
    for (int i = 0; i < positions.Length; i++)
    {
        var slot = i == 0 ? original : (XmlElement)original.CloneNode(true);
        var element = slot["Element"]!;
        element["Position"]!.InnerText = Hex(Ints(positions[i].Item2, positions[i].Item3));
        // Northern island retains vanilla label for quest lookups; distinguish the added copies.
        if (i > 0) element["IslandLabel"]!.InnerText = Hex(Encoding.UTF8.GetBytes("cinis_" + positions[i].Item1.ToLowerInvariant()));
        // Keep vanilla rotation until a runtime test establishes multi-instance behavior.
        if (i > 0) map.AppendChild(slot);
    }
    var resultSlots = map.SelectNodes("TemplateElement")!.Cast<XmlElement>().ToList();
    map["ElementCount"]!.InnerText = Hex(Ints(resultSlots.Count));
    Require(resultSlots.Count == slots.Count + 3, "Wrong element count");
    var layout = new List<object>();
    foreach (var slot in resultSlots)
    {
        var el = slot["Element"]!;
        var xy = Decode(el["Position"]!.InnerText);
        bool fixedIsland = el["MapFilePath"] != null;
        bool ship = slot["ElementType"]?.InnerText == "02000000";
        int sizeCode = el["Size"] == null || el["Size"]!.InnerText.Length == 0 ? 0 : BitConverter.ToInt16(Convert.FromHexString(el["Size"]!.InnerText));
        // Max MapSize from extracted Roman + DLC01 .a7minfo files (see research/island-sizes.json).
        int footprint = fixedIsland ? 768 : ship ? 0 : new[] {256, 320, 512, 512}[sizeCode];
        Require(xy[0] >= 20 && xy[1] >= 20 && xy[0] + footprint <= 4076 && xy[1] + footprint <= 4076, "Slot outside playable area");
        if (!fixedIsland && !ship)
            foreach (var p in positions)
                Require(!(xy[0] < p.Item2 + 768 && xy[0] + footprint > p.Item2 && xy[1] < p.Item3 + 768 && xy[1] + footprint > p.Item3), "Slot overlaps Cinis");
        layout.Add(new { x=xy[0], y=xy[1], size=footprint, kind=fixedIsland ? "Cinis" : ship ? "Start" : "Random", sizeCode,
            label=el["IslandLabel"] == null ? "" : Encoding.UTF8.GetString(Convert.FromHexString(el["IslandLabel"]!.InnerText)) });
    }
    var edited = new XmlFileDbConverter(FileDBDocumentVersion.Version3).ToFileDb(xml);
    Save(edited, args[2]);
    Equal(edited.Roots, Read(args[2]).Roots);
    File.WriteAllText(args[2] + ".layout.json", JsonSerializer.Serialize(layout, new JsonSerializerOptions { WriteIndented = true }));
    Console.WriteLine($"PASS: {resultSlots.Count} elements, four Cinis, other slots shifted +1024/+1024; binary roundtrip verified");
}
else throw new ArgumentException("Unknown command");

static IFileDBDocument Read(string path)
{
    using var stream = File.OpenRead(path);
    return new DocumentParser(FileDBDocumentVersion.Version3).LoadFileDBDocument(stream);
}
static void Save(IFileDBDocument doc, string path)
{
    Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
    using var stream = File.Create(path);
    new DocumentWriter().WriteFileDBToStream(doc, stream);
}
static FileDBNode Find(Tag root, string path)
{
    FileDBNode node = root;
    foreach (var part in path.Split('/')) node = ((Tag)node).Children.Single(n => n.Name == part);
    return node;
}
static void Set(Tag root, string path, byte[] bytes) => ((Attrib)Find(root, path)).Content = bytes;
static byte[] Ints(params int[] values) => values.SelectMany(BitConverter.GetBytes).ToArray();
static string Hex(byte[] bytes) => Convert.ToHexString(bytes);
static int[] Decode(string value)
{
    var bytes = Convert.FromHexString(value);
    return Enumerable.Range(0, bytes.Length / 4).Select(i => BitConverter.ToInt32(bytes, i * 4)).ToArray();
}
static void Require(bool condition, string message) { if (!condition) throw new InvalidDataException(message); }
static FileDBNode Clone(FileDBNode source, Tag parent)
{
    if (source is Attrib a) return new Attrib { ParentDoc=a.ParentDoc, Parent=parent, ID=a.ID, NodeType=a.NodeType, Content=a.Content.ToArray() };
    var t = (Tag)source;
    var copy = new Tag { ParentDoc=t.ParentDoc, Parent=parent, ID=t.ID, NodeType=t.NodeType };
    foreach (var child in t.Children) copy.AddChild(Clone(child, copy));
    return copy;
}
static void Equal(IReadOnlyList<FileDBNode> expected, IReadOnlyList<FileDBNode> actual)
{
    Require(expected.Count == actual.Count, "Roundtrip node count mismatch");
    for (int i = 0; i < expected.Count; i++)
    {
        Require(expected[i].Name == actual[i].Name && expected[i].NodeType == actual[i].NodeType, "Roundtrip node mismatch");
        if (expected[i] is Attrib a) Require(a.Content.AsSpan().SequenceEqual(((Attrib)actual[i]).Content), "Roundtrip payload mismatch: " + a.Name);
        else Equal(((Tag)expected[i]).Children, ((Tag)actual[i]).Children);
    }
}
