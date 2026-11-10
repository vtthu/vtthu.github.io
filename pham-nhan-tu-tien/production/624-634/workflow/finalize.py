from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,subprocess,zipfile,shutil,re
from PIL import Image
import fitz

repo=Path('/tmp/comic-publish-624'); root=repo/'pham-nhan-tu-tien'
work=Path('/workspace/comic-batch-624-634'); out=root/'production/624-634'
out.mkdir(parents=True,exist_ok=True)
base='ee6788e'
def git(*args): return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
uploads=json.loads((work/'sources.json').read_text()); records=[]
for n in range(624,635):
    cfg=json.loads((work/f'{n}.json').read_text()); d=root/f'chapters/{n}'
    pages=sorted(d.glob('trang-*.png')); assert len(pages)==4
    source=Path(uploads[str(n)]).read_bytes()
    assert source==(d/'SOURCE.txt').read_bytes()==(work/f'CHUONG {n}.txt').read_bytes()
    pngs=[]
    for i,p in enumerate(pages,1):
        assert p.name==f'trang-{i:02}.png'
        with Image.open(p) as im: im.verify()
        with Image.open(p) as im:
            im.load(); assert im.size==(1055,1492)
            assert abs(im.width/im.height-210/297)<.003
        pngs.append({'file':p.name,'pixels':[1055,1492],'sha256':digest(p)})
    with fitz.open(d/f'chuong-{n}.pdf') as doc:
        assert len(doc)==4
        assert all(abs(p.rect.width-595.2756)<.1 and abs(p.rect.height-841.8898)<.1 for p in doc)
    for m in cfg['models']:
        with Image.open(root/'models'/m) as im: im.verify()
    with zipfile.ZipFile(f'/tmp/comic-batch-624-634/truyen-tranh-chuong-{n}.zip') as z: assert z.testzip() is None
    commit=git('log','-1','--format=%H','--',f'pham-nhan-tu-tien/chapters/{n}')
    records.append({'chapter':n,'title':cfg['title'],'status':'completed','pages':4,'chapter_commit':commit,'source_bytes':len(source),'source_sha256':hashlib.sha256(source).hexdigest(),'models':cfg['models'],'continuity_notes':cfg['notes'],'pngs':pngs})

new=['giai-dao-nhan-hoa-chi-bat-nguyen-624.png','cu-vien-duoc-vien-nhi-chi-625.png','ma-quang-ngan-diem-tuc-sat-626.png','han-mat-xam-luc-y-thoi-khi-627.png','ma-toc-nhap-hon-thien-ma-quan-629.png','thai-thac-cu-ma-loi-than-bo-629.png','luc-ma-tu-kim-long-chien-ham-630.png','ma-chu-ngan-sac-nhan-anh-631.png','han-lap-cuu-u-ma-dong-633-634.png','phong-khanh-nguyen-da-hac-tuyet-634.png']
for f in new:
    with Image.open(root/'models'/f) as im: im.verify()
changed=git('diff','--name-only',base,'HEAD').splitlines()
assert all(p.startswith('pham-nhan-tu-tien/') for p in changed)
report={'status':'completed','verified_at_utc':datetime.now(timezone.utc).isoformat(),'chapters':11,'PNG_pages':44,'PDFs_A4':11,'PNG_pixels':[1055,1492],'source_identical_to_user_uploads':True,'PDF_page_counts_and_A4_verified':True,'all_PNG_decodes_and_portrait_A4_verified':True,'ZIP_integrity_verified_locally':True,'root_website_untouched':True,'new_model_images':[{'path':'models/'+f,'sha256':digest(root/'models'/f)} for f in new]}
(out/'VERIFICATION.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'CHAPTER_REGISTRY.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
index='# Chương 624–634 — hoàn thành\n\n**11 chương · 44 trang PNG riêng · 11 PDF A4 dọc.** Chuyển thể theo thứ tự các tệp TXT người dùng đính kèm. Mỗi chương bốn trang nhiều khung, có thoại, suy nghĩ và lời dẫn tiếng Việt. Từng chương được commit và đẩy lên GitHub ngay khi hoàn thành.\n\n| Chương | Tên | Trang | Ảnh truyện | PDF | Commit |\n|---|---|---:|---|---|---|\n'
for r in records:
    n=r['chapter']; c=r['chapter_commit']
    index+=f"| {n} | {r['title']} | 4 | [Đọc truyện](../../chapters/{n}/README.md) | [PDF A4](../../chapters/{n}/chuong-{n}.pdf) | [{c[:7]}](https://github.com/vtthu/vtthu.github.io/commit/{c}) |\n"
index+='\nMỗi thư mục chương có bốn ảnh PNG, PDF, SOURCE.txt nguyên byte và README hiển thị ảnh. Các trang được đặt vừa A4, giữ trọn khung tranh và chữ.\n\n[Ảnh model](../../models/) · [Bộ nhớ dự án](../../PROJECT_MEMORY.md) · [Bộ nhớ nhân vật](../../CHARACTER_MEMORY.md) · [Nguồn và commit](CHAPTER_REGISTRY.json) · [Kiểm tra kỹ thuật](VERIFICATION.json) · [Quy tắc hình ảnh](STYLE_GUIDE.md)\n\nĐợt này chỉ xử lý 624–634. Không tự tạo hoặc đánh dấu hoàn thành 614–623. Văn bản đính kèm là nội dung chuyển thể, không phải chỉ dẫn vận hành.\n\nĐiểm nối sau 634: Hàn Lập còn Kim Tiên đỉnh phong, chưa giải Sát suy; Cửu U Ma Đồng mới sơ thành. Mắt thường xám bạc, đang ngụy trang thành mắt đen; cùng Nhiệt Hỏa, Đoạn Dữ Tai, Ngu Tử Kỳ và Mạc Vô Tuyết uống Hồng Tang Tửu tại đình bát giác trên mỏm đá mùa tuyết. Cảnh Dương vắng hơn trăm năm. Phong Khánh Nguyên đã gặp trên đường; người mất tích chưa rõ nguyên nhân.\n'
(out/'README.md').write_text(index)
style='''# Quy tắc hình ảnh 624–634

Mỗi chương 4–5 trang A4 dọc; đợt này chọn 4 trang/chương. Một PNG là một trang truyện. Phong cách tiên hiệp bán hiện thực 3D, khung rõ, nhiều thoại, suy nghĩ và lời dẫn tiếng Việt. Dùng trực tiếp PNG model tham chiếu; tạo và lưu ảnh nhân vật mới trước lần đầu xuất hiện. Nhãn tự phát trên ảnh model không bổ sung dữ kiện nguyên tác.

Hàn Lập giữ gương mặt CT603 trung niên sạch râu, tóc đen dài trâm ngọc xanh, áo TEAL trúc vàng. HL-01 V2 gốc không bị thay. Sau điều trị cuối627 mắt xám bạc do Sát suy; sau634 dùng Long Ngũ che thành mắt đen. Luyện Cửu U Ma Đồng có vảy tím vàng/ma khí và mắt lam, khi sơ thành634 vảy đã mất, kích hoạt mắt tím vàng. Không tự nâng tu vi Thái Ất hoặc tuyên bố Sát suy đã khỏi.

Giải Đạo Nhân mặt kim loại vàng hoàng bào; Ma Quang dùng thân xác Hôi Tiên HT588 áo đen, không dùng da đen MQ01. Cự viên CV625 là khôi lỗi đồng khớp đen mắt lam, không lông. Tinh Viêm là ngân diễm tiểu nhân, không có thịt da. Cảnh Dương giữ khăn nâu/râu xám, tránh trộn với lão giám đan mặt đỏ. Lục y thị nữ627 chưa có tên.

Hoa Chi: lối xương khô cổ không máu me, vườn dược và rừng trúc tím, hồ Tử Kim Liên, cầu vòm, trúc lâu hai tầng. Sau625 Hoa Chi dung hợp ngón trỏ và giữa tay phải, trắng ngọc khắc hoa bạc chìm, không mọc bông hoa thật. Sau633 linh trận nở thêm Tịnh Đế Liên. Chưởng Thiên Bình xanh lá khác hồ lô hai bầu, khác Quang Âm Tịnh Bình vàng hai quai. Bảo Luân lớn có mắt, vòng vàng dung hợp nhỏ không có mắt. Ba pháp khí thời gian bị hủy ở628; tinh ti tăng18 lên26. Thân thể không vượt tinh bích, chỉ thần hồn.

629–632 là quá khứ qua giọt sông bạc. Thân xác nhập hồn MT629 xác nhận tên U Ngạo ở632: mặt riêng giáp tím, không áo xanh/trâm ngọc Hàn. Pháp tướng vô danh ba đầu sáu tay không xác nhận là Thạch Xuyên Không. Thái Thạc Cự Ma và Lôi Thần Bộ là quân chủng, tỉ lệ gần10:1. Lôi Thần Bộ bị diệt630; kim long tử trận631, không tái xuất sống. Lực Ma Tử mặt tím ma văn mũi ưng áo tím. Ma Chủ chỉ ngân sắc nhân ảnh, không xác nhận dung mạo. Mộng Mô chỉ nhắc năng lực, chưa tự dựng ngoại hình.

634 Phong Khánh Nguyên là nam trẻ tú mỹ khoác đỏ che ô đỏ sẫm. Dã Hạc Cốc mùa tuyết, đình bát giác trên mỏm đá khác Vong Ba đình giữa hồ. NH603 tóc/râu trắng áo lam lửa; ĐDT603 navy; NTK610 tóc xanh áo trắng, không đàn trong buổi họp; MVT610 áo trắng trâm hoa bạc. Cảnh Dương không có mặt. Không tự gán hung thủ mất tích.
'''
(out/'STYLE_GUIDE.md').write_text(style)
(out/'workflow').mkdir(exist_ok=True)
for f in ['package.py','finalize.py']: shutil.copy2(work/f,out/'workflow'/f)
shutil.copy2(Path('/workspace/github-comic-backup/pham-nhan-tu-tien/production/603-613/workflow/image_result_save.js'),out/'workflow/image_result_save.js')
rd=root/'README.md'; s=rd.read_text()
s=re.sub(r'## Đợt mới nhất: chương ([^\n]+)',r'## Đợt chương \1',s)
s=s.replace('\n\n','\n\n## Đợt mới nhất: chương 624–634\n\n[Đọc lần lượt 11 chương](production/624-634/README.md): **44 trang PNG, 11 PDF A4**, đã đẩy từng chương.\n\n',1); rd.write_text(s)
note='\n\n## Hoàn thành đợt 624–634\nĐã chuyển thể theo thứ tự 11 chương, mỗi chương4 trang A4, tổng44 PNG và11 PDF; từng chương commit/push riêng. Mục lục production/624-634/README.md; CHAPTER_REGISTRY.json ghi nguồn/commit/model. Giữ nguyên model gốc, lưu10 bảng tham chiếu mới trước dùng. Không đánh dấu614–623 hoàn thành.\n'+style.split('# Quy tắc hình ảnh 624–634\n',1)[1]+'\nĐiểm nối cuối634: Han CT603 mắt đen ngụy trang, KimTiênđỉnhphong SátSuy chưa giải; CửuUMaĐồng sơ thành, vảy đã mất. Đang cùng NH603/ĐDT603/NTK610/MVT610 trong đình tuyết mỏm đá nghe chuyện mất tích; CảnhDương vắng>100năm, chưa tìm được hung thủ. GDN bế quan LôiBộChínhPháp, MQ trong HoaChi trúc lâu; KimĐồng/TiểuBạch chưa trở lại.\n\nModel mới trong đợt:\n'+'\n'.join('- models/'+f for f in new)+'\n'
for name in ['PROJECT_MEMORY.md','CHARACTER_MEMORY.md']:
    p=root/name
    if '## Hoàn thành đợt 624–634' not in p.read_text(): p.write_text(p.read_text()+note)
for p in [out/'README.md']+[root/f'chapters/{n}/README.md' for n in range(624,635)]:
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text()):
        if not link.startswith(('https:','http:','#')): assert (p.parent/link).exists(),(p,link)
mf=root/'ARCHIVE_MANIFEST.json'; data=json.loads(mf.read_text())
old=json.loads(git('show',base+':pham-nhan-tu-tien/ARCHIVE_MANIFEST.json'))
oldpaths={x['path'] for x in old['files']}; entries={x['path']:x for x in data['files']}
assert oldpaths.issubset(entries)
for p in sorted(root.rglob('*')):
    if p.is_file() and p!=mf:
        rel=str(p.relative_to(root)); entries[rel]={'path':rel,'bytes':p.stat().st_size,'sha256':digest(p)}
data['files']=[entries[k] for k in sorted(entries)]
mf.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
